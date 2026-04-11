#exonware/xwapi/engines/grpc.py
"""
gRPC Server Engine Implementation
gRPC-based API server engine using Protocol Buffers.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.6
"""

from typing import Any
import threading
import os
import sys
import tempfile
import importlib.util
import inspect
from .base import AApiServerEngineBase
from .contracts import ProtocolType
from exonware.xwapi.config import XWAPIConfig
from exonware.xwsystem import get_logger
logger = get_logger(__name__)


class GrpcServerEngine(AApiServerEngineBase):
    """
    gRPC Server Engine
    Implements API server using gRPC (HTTP/2 + Protocol Buffers).
    Supports automatic proto generation and service registration.
    """

    def __init__(self):
        """Initialize gRPC server engine."""
        super().__init__("grpc")
        self._server: Any | None = None
        self._protocol_type = ProtocolType.GRPC
        self._registered_actions: list[Any] = []
        self._generated_proto_path: str | None = None
    @property

    def protocol_type(self) -> ProtocolType:
        """Get protocol type (GRPC)."""
        return self._protocol_type
    @property

    def supports_admin_endpoints(self) -> bool:
        """gRPC doesn't support HTTP admin endpoints."""
        return False

    def create_app(self, config: XWAPIConfig) -> Any:
        """
        Create gRPC server.
        Args:
            config: XWAPI configuration
        Returns:
            gRPC server instance
        """
        try:
            import grpc
            from concurrent import futures
        except ImportError:
            raise ImportError(
                "grpcio is required for GrpcServerEngine. "
                "Install with: pip install grpcio grpcio-tools"
            )
        # Create gRPC server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self._server = server
        self._config = config
        return server

    def register_action(self, app: Any, action: Any, 
                       route_info: dict[str, Any]) -> bool:
        """
        Register XWAction as gRPC service method.
        Args:
            app: gRPC server instance
            action: XWAction instance
            route_info: Must contain 'service' and 'method' keys
        Returns:
            True (registration is deferred to start_server)
        """
        service_name = route_info.get('service', 'DefaultService')
        method_name = route_info.get('method', getattr(action, 'api_name', 'Unknown'))
        # Store for later processing
        self._registered_actions.append({
            'action': action,
            'service': service_name,
            'method': method_name
        })
        logger.debug(f"Queued gRPC action {service_name}.{method_name}")
        return True

    def generate_schema(self, app: Any, actions: list[Any], 
                        config: XWAPIConfig) -> dict[str, Any]:
        """
        Generate Protocol Buffer schema for gRPC.
        """
        proto_content = self._generate_proto_content(self._registered_actions, config)
        return {
            "proto_file": proto_content,
            "services": self._extract_services(self._registered_actions),
        }

    def _generate_proto_content(self, actions_info: list[dict], config: XWAPIConfig) -> str:
        """Generate .proto file content from actions."""
        lines = [
            'syntax = "proto3";',
            f'package {getattr(config, "title", "api").lower().replace(" ", "_")};',
            '',
            f'// Generated API for {getattr(config, "title", "API")}',
            '',
        ]
        # Group by service
        services = {}
        for item in actions_info:
            svc = item['service']
            if svc not in services:
                services[svc] = []
            services[svc].append(item)
        # 1. Generate Messages
        generated_messages = set()
        for svc, items in services.items():
            for item in items:
                method = item['method']
                action = item['action']
                # Request Message
                req_msg_name = f"{method}Request"
                if req_msg_name not in generated_messages:
                    lines.append(f"message {req_msg_name} {{")
                    in_types = getattr(action, 'in_types', {}) or {}
                    i = 1
                    for arg_name, schema in in_types.items():
                        proto_type = self._map_schema_to_proto_type(schema)
                        lines.append(f"  {proto_type} {arg_name} = {i};")
                        i += 1
                    lines.append("}")
                    lines.append("")
                    generated_messages.add(req_msg_name)
                # Response Message
                resp_msg_name = f"{method}Response"
                if resp_msg_name not in generated_messages:
                    lines.append(f"message {resp_msg_name} {{")
                    out_types = getattr(action, 'out_types', {}) or {}
                    i = 1
                    if out_types:
                        for field_name, schema in out_types.items():
                             proto_type = self._map_schema_to_proto_type(schema)
                             lines.append(f"  {proto_type} {field_name} = {i};")
                             i += 1
                    else:
                        # Default generic response if no out_types
                        lines.append("  string result_json = 1;")
                    lines.append("}")
                    lines.append("")
                    generated_messages.add(resp_msg_name)
        # 2. Generate Services
        for svc, items in services.items():
            lines.append(f"service {svc} {{")
            for item in items:
                method = item['method']
                lines.append(f"  rpc {method}({method}Request) returns ({method}Response);")
            lines.append("}")
            lines.append("")
        return "\n".join(lines)

    def _map_schema_to_proto_type(self, schema: Any) -> str:
        """Map XWSchema to proto type."""
        # Simplified mapping
        schema_dict = schema
        if hasattr(schema, 'definition'):
             schema_dict = schema.definition
        elif hasattr(schema, 'schema'):
             schema_dict = schema.schema
        if not isinstance(schema_dict, dict):
            return "string"
        t = schema_dict.get('type', 'string')
        if t == 'string': return "string"
        if t == 'integer': return "int32"
        if t == 'number': return "float"
        if t == 'boolean': return "bool"
        # Nested/Arrays are complex -> string (json) for now to be safe
        # Or generic Struct?
        return "string" 

    def _extract_services(self, actions_info: list[dict]) -> dict[str, list[str]]:
        services = {}
        for item in actions_info:
            svc = item['service']
            if svc not in services:
                services[svc] = []
            services[svc].append(item['method'])
        return services

    def start_server(self, app: Any, host: str = "0.0.0.0", 
                    port: int = 50051, max_workers: int = 10, **kwargs) -> None:
        """
        Start gRPC server.
        Generates proto, compiles it, and registers services.
        """
        import grpc
        from grpc_tools import protoc
        # 1. Generate .proto
        config = getattr(self, '_config', None) or kwargs.get('config') or XWAPIConfig()
        if not hasattr(config, 'title'):
            # Fallback mock config if not provided
            class Cfg: title="API"
            config = Cfg()
        proto_content = self._generate_proto_content(self._registered_actions, config)
        # 2. Write and Compile
        with tempfile.TemporaryDirectory() as tmpdir:
            proto_path = os.path.join(tmpdir, "service.proto")
            with open(proto_path, "w") as f:
                f.write(proto_content)
            # Run protoc
            args = [
                'grpc_tools.protoc',
                f'-I{tmpdir}',
                f'--python_out={tmpdir}',
                f'--grpc_python_out={tmpdir}',
                proto_path
            ]
            exit_code = protoc.main(args)
            if exit_code != 0:
                logger.error("Failed to compile generated proto file")
                return
            # 3. Load generated modules
            sys.path.append(tmpdir)
            try:
                import service_pb2 as pb2
                import service_pb2_grpc as pb2_grpc
            except ImportError as e:
                logger.error(f"Failed to import generated proto modules: {e}")
                return
            # 4. Implement Servicers
            services = self._extract_services(self._registered_actions)
            for svc_name, methods in services.items():
                servicer_base = getattr(pb2_grpc, f"{svc_name}Servicer", None)
                adder = getattr(pb2_grpc, f"add_{svc_name}Servicer_to_server", None)
                if not servicer_base or not adder:
                    logger.warning(f"Could not find generated classes for {svc_name}")
                    continue
                # Dynamic Servicer Class
                class DynamicServicer(servicer_base):
                    def __init__(self, engine):
                        self.engine = engine
                # Add methods to class
                for method_name in methods:
                    # Find action
                    action_info = next(
                        (i for i in self._registered_actions 
                         if i['service'] == svc_name and i['method'] == method_name), 
                        None
                    )
                    if not action_info: continue
                    action = action_info['action']
                    def make_rpc_method(act, m_name):
                        def rpc_method(self, request, context):
                            # Unpack request
                            kwargs = {}
                            # Simplified: iterate fields in request
                            # In real proto, accessing fields is explicit
                            # We can convert message to dict
                            from google.protobuf.json_format import MessageToDict
                            req_dict = MessageToDict(request, preserving_proto_field_name=True)
                            # Invoke action
                            try:
                                if inspect.iscoroutinefunction(act.__call__):
                                    # gRPC python sync server cannot await?
                                    # We created a ThreadPoolExecutor server.
                                    # If action is async, we need to run it in event loop?
                                    # For simplicity, assume sync or run in loop
                                    import asyncio
                                    try:
                                        loop = asyncio.get_event_loop()
                                    except RuntimeError:
                                        loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(loop)
                                    result = loop.run_until_complete(act(**req_dict))
                                else:
                                    result = act(**req_dict)
                            except Exception as e:
                                context.set_details(str(e))
                                context.set_code(grpc.StatusCode.INTERNAL)
                                # return empty response?
                                resp_cls = getattr(pb2, f"{m_name}Response")
                                return resp_cls()
                            # Pack Response
                            resp_cls = getattr(pb2, f"{m_name}Response")
                            # If result is dict, convert. If primitive...
                            if isinstance(result, dict):
                                return resp_cls(**result)
                            elif hasattr(result, '__dict__'):
                                return resp_cls(**result.__dict__)
                            else:
                                # Single field response? logic needed
                                # For now assume dict or empty
                                return resp_cls()
                        return rpc_method
                    setattr(DynamicServicer, method_name, make_rpc_method(action, method_name))
                # Instantiate and Register
                servicer = DynamicServicer(self)
                adder(servicer, app)
                logger.info(f"Registered gRPC service: {svc_name}")
            # Remove tmpdir from path? 
            # Ideally yes, but we might need it while running.
            # Since we wait_for_termination inside this scope (if we do), tmpdir stays alive?
            # NO, context manager exits.
            # We must persist the tmpdir or generated files if we want them to survive.
            # But here we import modules. Once imported, they are in memory.
            # However, if we exit context, files are deleted. Python might lazy load?
            # Safer to keep files or load everything.
            pass 
        # Start Server
        listen_addr = f'{host}:{port}'
        app.add_insecure_port(listen_addr)
        logger.info(f"Starting gRPC server on {listen_addr}")
        app.start()
        try:
            app.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("gRPC server interrupted")
            app.stop(grace=5)

    def stop_server(self, app: Any) -> None:
        """Stop gRPC server."""
        if app:
            logger.info("Stopping gRPC server")
            app.stop(grace=5)
