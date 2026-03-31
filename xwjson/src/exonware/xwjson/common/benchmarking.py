#!/usr/bin/env python3
"""
#exonware/xwjson/src/exonware/xwjson/common/benchmarking.py
Performance Benchmarking Utilities for XWJSON
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.9.0.11
Generation Date: 15-Nov-2025
"""

import time
import statistics
from typing import Any
from dataclasses import dataclass
from exonware.xwsystem import get_logger
logger = get_logger(__name__)
@dataclass

class XWJSONBenchmarkResult:
    """Result of an XWJSON benchmark."""
    operation: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    median_time: float
    std_dev: float
    throughput: float  # operations per second
    file_size: int | None = None


class XWJSONBenchmark:
    """Benchmark utilities for XWJSON operations."""
    @staticmethod

    def benchmark_encode(
        data: Any,
        iterations: int = 1000,
        warmup: int = 100
    ) -> XWJSONBenchmarkResult:
        """
        Benchmark XWJSON encoding operation.
        Args:
            data: Data to encode
            iterations: Number of iterations
            warmup: Number of warmup iterations
        Returns:
            XWJSONBenchmarkResult with statistics
        """
        from ..formats.binary.xwjson.serializer import XWJSONSerializer
        serializer = XWJSONSerializer()
        # Warmup
        for _ in range(warmup):
            try:
                serializer.encode(data)
            except Exception:
                pass
        # Actual benchmark
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                serializer.encode(data)
            except Exception as e:
                logger.warning(f"Encode operation failed: {e}")
            end = time.perf_counter()
            times.append(end - start)
        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        throughput = iterations / total_time if total_time > 0 else 0.0
        # Get file size
        try:
            encoded = serializer.encode(data)
            file_size = len(encoded)
        except Exception:
            file_size = None
        return XWJSONBenchmarkResult(
            operation="encode",
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            std_dev=std_dev,
            throughput=throughput,
            file_size=file_size
        )
    @staticmethod

    def benchmark_decode(
        encoded_data: bytes,
        iterations: int = 1000,
        warmup: int = 100
    ) -> XWJSONBenchmarkResult:
        """
        Benchmark XWJSON decoding operation.
        Args:
            encoded_data: Encoded data to decode
            iterations: Number of iterations
            warmup: Number of warmup iterations
        Returns:
            XWJSONBenchmarkResult with statistics
        """
        from ..formats.binary.xwjson.serializer import XWJSONSerializer
        serializer = XWJSONSerializer()
        # Warmup
        for _ in range(warmup):
            try:
                serializer.decode(encoded_data)
            except Exception:
                pass
        # Actual benchmark
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                serializer.decode(encoded_data)
            except Exception as e:
                logger.warning(f"Decode operation failed: {e}")
            end = time.perf_counter()
            times.append(end - start)
        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        throughput = iterations / total_time if total_time > 0 else 0.0
        return XWJSONBenchmarkResult(
            operation="decode",
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            median_time=median_time,
            std_dev=std_dev,
            throughput=throughput,
            file_size=len(encoded_data)
        )
