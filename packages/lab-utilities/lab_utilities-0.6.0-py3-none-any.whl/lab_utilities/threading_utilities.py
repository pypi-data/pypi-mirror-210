# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 18:55:40 2023

@author: stefa
"""
from threading import Thread

class RaisingThread(Thread):
  def run(self):
    self._exc = None
    try:
      super().run()
    except Exception as e:
      self._exc = e

  def join(self, timeout=None):
    super().join(timeout=timeout)
    if self._exc:
      raise self._exc

def run_async(funcs):
    def go():
        try:
            iter(funcs)
        except TypeError:
            funcs()
            return
        for func in funcs:
            func()
    func_thread = RaisingThread(target=go, daemon=True)
    func_thread.start()
    return func_thread

def run_async_dict(func):
    def go():
        func['function'](func['arguments'])
        return
    func_thread = RaisingThread(target=go, daemon=True)
    func_thread.start()
    return func_thread
