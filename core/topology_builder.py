#!/usr/bin/env python3
import argparse
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
from sklearn.cluster import KMeans

# Willow imports
from core import topology
from core.database import get_db_connection
from core.utils import setup_logging, safe_db_operation

# Constants
DEFAULT_INTERVAL = 3600  # 1 hour in seconds
LOG_FILE = Path("core/topology_build.log")
DB_CONNECTION_TIMEOUT = 30

class TopologyBuilderDaemon:
    def __init__(self, interval: int = DEFAULT_INTERVAL, full_rebuild: bool = False):
        self.interval = interval
        self.full_rebuild = full_rebuild
        self.running = False
        self.logger = logging.getLogger(__name__)

    def setup_logging(self):
        setup_logging(
            log_file=LOG_FILE,
            log_level=logging.INFO,
            console=True,
            json_format=False
        )

    def handle_signal(self, signum, frame):
        self.logger.info("Received shutdown signal, stopping gracefully...")
        self.running = False

    def build_edges(self):
        """Build knowledge graph edges between atoms."""
        start_time = time.time()
        try:
            with safe_db_operation(get_db_connection, timeout=DB_CONNECTION_TIMEOUT) as db:
                edges = topology.build_edges(db, full=self.full_rebuild)
                edge_count = len(edges)
                self.logger.info(f"Built {edge_count} edges in {time.time() - start_time:.2f}s")
                return edges
        except Exception as e:
            self.logger.error(f"Error building edges: {str(e)}")
            return []

    def cluster_atoms(self, edges):
        """Cluster atoms using KMeans."""
        start_time = time.time()
        try:
            with safe_db_operation(get_db_connection, timeout=DB_CONNECTION_TIMEOUT) as db:
                clusters = topology.cluster_atoms(db, edges)
                cluster_count = len(clusters)
                self.logger.info(f"Created {cluster_count} clusters in {time.time() - start_time:.2f}s")
                return clusters
        except Exception as e:
            self.logger.error(f"Error clustering atoms: {str(e)}")
            return []

    def run(self):
        """Main daemon loop."""
        self.running = True
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        self.logger.info(f"Starting topology builder daemon (interval: {self.interval}s, full_rebuild: {self.full_rebuild})")

        while self.running:
            try:
                self.logger.info("Starting topology build cycle")
                edges = self.build_edges()
                if edges:
                    clusters = self.cluster_atoms(edges)
                else:
                    self.logger.warning("No edges built, skipping clustering")

                if not self.running:
                    break

                self.logger.info(f"Sleeping for {self.interval} seconds")
                time.sleep(self.interval)

            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                time.sleep(min(self.interval, 60))  # Don't spam on errors

        self.logger.info("Topology builder daemon stopped")

def parse_args():
    parser = argparse.ArgumentParser(description="Topology Builder Daemon")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                        help=f"Interval between builds in seconds (default: {DEFAULT_INTERVAL})")
    parser.add_argument("--daemon", action="store_true",
                        help="Run as a daemon (continuous operation)")
    parser.add_argument("--full", action="store_true",
                        help="Perform a full rebuild of all edges")
    return parser.parse_args()

def main():
    args = parse_args()
    builder = TopologyBuilderDaemon(interval=args.interval, full_rebuild=args.full)
    builder.setup_logging()

    if args.daemon:
        builder.run()
    else:
        # Single run mode
        builder.build_edges()
        builder.cluster_atoms(builder.build_edges())

if __name__ == "__main__":
    main()
