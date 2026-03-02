#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
⚙️ Production Worker - Efficient Task Execution
═══════════════════════════════════════════════════════════════
- Uses ThreadPoolExecutor for controlled parallelism
- Optimized for limited CPU resources (0.5 CPU on Render)
- Task queue with worker threads
- Graceful shutdown handling
═══════════════════════════════════════════════════════════════
"""
import os
import sys
import time
import signal
import threading
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import logger
from database.connection import DatabaseConnection

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 3))  # Limited for 0.5 CPU
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', 5))  # 5 seconds
QUEUE_SIZE = int(os.getenv('QUEUE_SIZE', 10))

# ═══════════════════════════════════════════════════════════════
# Job Registry
# ═══════════════════════════════════════════════════════════════
def import_job_functions():
    """Import all job functions"""
    try:
        from worker_scraper import ScraperWorker
        from worker_audio import AudioWorker
        from worker_video import VideoWorker
        
        return {
            'scraper': lambda: ScraperWorker(interval=600).run_once(),
            'audio': lambda: AudioWorker(interval=120).run_once(),
            'video': lambda: VideoWorker(interval=120).run_once(),
        }
    except Exception as e:
        logger.error(f"❌ Error importing job functions: {e}")
        return {}

# ═══════════════════════════════════════════════════════════════
# Task Management
# ═══════════════════════════════════════════════════════════════
class TaskManager:
    """Manages task scheduling and execution"""
    
    def __init__(self):
        self.last_scraper_run = 0
        self.last_audio_run = 0
        self.last_video_run = 0
        
        # Intervals in seconds
        self.scraper_interval = 600  # 10 minutes
        self.audio_interval = 120    # 2 minutes
        self.video_interval = 120    # 2 minutes
    
    def get_due_tasks(self):
        """Get list of tasks that are due to run"""
        current_time = time.time()
        due_tasks = []
        
        # Check scraper task
        if current_time - self.last_scraper_run >= self.scraper_interval:
            due_tasks.append({
                'type': 'scraper',
                'name': 'Scraper Job',
                'emoji': '📰'
            })
            self.last_scraper_run = current_time
        
        # Check audio task
        if current_time - self.last_audio_run >= self.audio_interval:
            due_tasks.append({
                'type': 'audio',
                'name': 'Audio Processing Job',
                'emoji': '🎙️'
            })
            self.last_audio_run = current_time
        
        # Check video task
        if current_time - self.last_video_run >= self.video_interval:
            due_tasks.append({
                'type': 'video',
                'name': 'Video Processing Job',
                'emoji': '🎬'
            })
            self.last_video_run = current_time
        
        return due_tasks

# ═══════════════════════════════════════════════════════════════
# Job Execution
# ═══════════════════════════════════════════════════════════════
def execute_job(task, job_func):
    """Execute a single job"""
    task_type = task['type']
    task_name = task['name']
    emoji = task['emoji']
    
    started_at = datetime.now()
    logger.info(f"{emoji} Executing: {task_name}")
    
    try:
        # Execute the job
        result = job_func()
        
        finished_at = datetime.now()
        execution_time = (finished_at - started_at).total_seconds()
        
        logger.info(f"✅ {task_name} completed in {execution_time:.1f}s")
        return {
            'success': True,
            'result': str(result) if result else 'completed',
            'execution_time': execution_time
        }
        
    except Exception as e:
        finished_at = datetime.now()
        execution_time = (finished_at - started_at).total_seconds()
        error_msg = str(e)
        
        logger.error(f"❌ {task_name} failed in {execution_time:.1f}s: {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'execution_time': execution_time
        }

# ═══════════════════════════════════════════════════════════════
# Worker Thread Function
# ═══════════════════════════════════════════════════════════════
def worker_thread(task_queue, job_registry, worker_id):
    """Worker thread that processes tasks from the queue"""
    logger.info(f"🚀 Worker thread {worker_id} started")
    
    while True:
        try:
            # Get task from queue (blocking with timeout)
            task = task_queue.get(timeout=1)
            
            task_type = task['type']
            
            # Check if job function exists
            if task_type not in job_registry:
                logger.error(f"❌ Unknown job type: {task_type}")
                task_queue.task_done()
                continue
            
            # Execute the job
            job_func = job_registry[task_type]
            result = execute_job(task, job_func)
            
            # Mark task as done
            task_queue.task_done()
            
        except Empty:
            # No task in queue, continue
            continue
        except Exception as e:
            logger.error(f"❌ Worker {worker_id} error: {e}")
            traceback.print_exc()
            task_queue.task_done()

# ═══════════════════════════════════════════════════════════════
# Main Worker
# ═══════════════════════════════════════════════════════════════
# Global flag for graceful shutdown
running = True
jobs_executed = 0

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global running
    logger.info("⚠️ Shutdown signal received, finishing current jobs...")
    running = False

def main():
    """Main worker loop"""
    global running, jobs_executed
    
    logger.info("═" * 70)
    logger.info("⚙️ Production Worker Starting")
    logger.info("   ✅ ThreadPoolExecutor for controlled parallelism")
    logger.info("   ✅ Optimized for limited CPU resources")
    logger.info("   ✅ Task queue with worker threads")
    logger.info("═" * 70)
    logger.info(f"Max workers: {MAX_WORKERS}")
    logger.info(f"Poll interval: {POLL_INTERVAL}s")
    logger.info("═" * 70)
    
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Import job functions
    job_registry = import_job_functions()
    if not job_registry:
        logger.error("❌ Failed to import job functions, exiting")
        sys.exit(1)
    
    logger.info(f"📋 Loaded {len(job_registry)} job types:")
    for job_type in sorted(job_registry.keys()):
        logger.info(f"   - {job_type}")
    logger.info("═" * 70)
    
    # Initialize task manager
    task_manager = TaskManager()
    
    # Create task queue
    task_queue = Queue(maxsize=QUEUE_SIZE)
    
    # Start worker threads
    threads = []
    for i in range(MAX_WORKERS):
        t = threading.Thread(
            target=worker_thread,
            args=(task_queue, job_registry, i + 1),
            daemon=True
        )
        t.start()
        threads.append(t)
        logger.info(f"🚀 Started worker thread {i + 1}/{MAX_WORKERS}")
    
    logger.info("═" * 70)
    logger.info("✅ All worker threads started, beginning task scheduling...")
    
    last_heartbeat = time.time()
    
    # Main scheduling loop
    while running:
        try:
            # Get due tasks
            due_tasks = task_manager.get_due_tasks()
            
            # Add due tasks to queue
            for task in due_tasks:
                try:
                    task_queue.put(task, timeout=1)
                    logger.info(f"📋 Queued: {task['name']}")
                    jobs_executed += 1
                except:
                    logger.warning(f"⚠️ Queue full, skipping {task['name']}")
            
            # Heartbeat every minute
            current_time = time.time()
            if current_time - last_heartbeat >= 60:
                logger.info(f"💓 Worker alive - {jobs_executed} jobs scheduled, queue size: {task_queue.qsize()}")
                last_heartbeat = current_time
            
            # Sleep before next poll
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("⚠️ Keyboard interrupt received")
            break
        except Exception as e:
            logger.error(f"❌ Main loop error: {e}")
            traceback.print_exc()
            time.sleep(POLL_INTERVAL)
    
    # Graceful shutdown
    logger.info("🛑 Shutting down gracefully...")
    
    # Wait for queue to empty
    logger.info("⏳ Waiting for current jobs to finish...")
    task_queue.join()
    
    logger.info("═" * 70)
    logger.info("🛑 Worker stopped gracefully")
    logger.info(f"📊 Total jobs scheduled: {jobs_executed}")
    logger.info("═" * 70)

if __name__ == "__main__":
    main()