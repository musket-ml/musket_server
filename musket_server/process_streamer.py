import os

import sys

import io

import shlex

import asyncio

import time

import threading

import requests

import subprocess

class Streamer:
    def __init__(self, timeout, logger):
        self.logger = logger

        self.timeout = timeout

        self.lines = ""

        self.expired = time.time() + timeout

        self.running = True

        self.thread = threading.Thread(target=self.listen)

        self.thread.start()

    def write_line(self, line):
        self.lines += line

    def stop(self):
        self.running = False

    def send(self):
        if len(self.lines):
            self.logger(self.lines)

            self.lines = ""

    def listen(self):
        while self.running:
            current_time = time.time()

            if current_time > self.expired:
                self.send()

                self.expired = current_time + self.timeout

            time.sleep(1)

        self.send()

def handle_streams(process, streamer):
    for line_encoded in process.stdout:
        line = line_encoded.decode()

        if line != '':
            streamer.write_line(line)

def stream_subprocess(cmd, streamer, cwd, process_setter, skip_upload = False):
    os.environ["PATH"]=os.environ["PATH"] + ":/Users/dreamflyer/.conda/envs/surf360cam/bin"

    print("TASK START")

    if not skip_upload:
        process = subprocess.Popen(["musket", "deps_download"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, bufsize=0)

        process.terminated = False

        process_setter(process)

        handle_streams(process, streamer)

    if skip_upload or not process.terminated:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, bufsize=0)

        process_setter(process)

        handle_streams(process, streamer)

    streamer.write_line("report_end")

    streamer.stop()

def execute(command_line, streamer, cwd, process_setter, skip_upload = False):
    stream_subprocess(shlex.split(command_line), streamer, cwd, process_setter, skip_upload)

def execute_command(command_line, cwd, logger, process_setter, skip_upload = False, stream_sleep = 10):
    print("executing: " + command_line)

    execute(command_line, Streamer(stream_sleep, logger), cwd, process_setter, skip_upload)


