#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:owefsad
# datetime:2021/1/26 下午4:05
# software: PyCharm
# project: lingzhi-engine

class VulEngine(object):
    """
    根据策略和方法池查找是否存在漏洞，此类不进行策略和方法池的权限验证
    """

    def __init__(self):
        """
        构造函数，初始化相关数据
        """
        self._method_pool = None
        self._vul_method_signature = None
        self.hit_vul = False
        self.vul_stack = None
        self.pool_value = None
        self.vul_source_signature = None

    @property
    def method_pool(self):
        """
        方法池数据
        :return:
        """
        return self._method_pool

    @method_pool.setter
    def method_pool(self, method_pool):
        """
        设置方法池数据，根据方法调用ID对数据进行倒序排列，便于后续检索漏洞
        :param method_pool:
        :return:
        """
        self._method_pool = sorted(method_pool, key=lambda e: e.__getitem__('invokeId'), reverse=True)

    @property
    def vul_method_signature(self):
        return self._vul_method_signature

    @vul_method_signature.setter
    def vul_method_signature(self, vul_method_signature):
        self._vul_method_signature = vul_method_signature

    def prepare(self, method_pool, vul_method_signature):
        """
        对方法池、漏洞方法签名及其他数据进行预处理
        :param method_pool: 方法池，list
        :param vul_method_signature: 漏洞方法签名，str
        :return:
        """
        self.method_pool = method_pool
        self.vul_method_signature = vul_method_signature
        self.hit_vul = False
        self.vul_stack = list()
        self.pool_value = -1
        self.vul_source_signature = ''

    def hit_vul_method(self, method):
        if f"{method.get('className')}.{method.get('methodName')}" == self.vul_method_signature:
            self.hit_vul = True
            self.vul_stack.append(method)
            self.pool_value = method.get('sourceHash')
            return True

    def do_propagator(self, method):
        is_source = method.get('source')
        target_hash = method.get('targetHash')

        if is_source:
            for hash in target_hash:
                if hash in self.pool_value:
                    self.vul_stack.append(method)
                    self.vul_source_signature = f"{method.get('className')}.{method.get('methodName')}"
                    break
        else:
            for hash in target_hash:
                if hash in self.pool_value:
                    self.vul_stack.append(method)
                    self.pool_value = method.get('sourceHash')
                    break

    def search(self, method_pool, vul_method_signature):
        self.prepare(method_pool, vul_method_signature)
        for method in self.method_pool:
            if not self.hit_vul and self.hit_vul_method(method):
                continue
            if self.hit_vul:
                self.do_propagator(method)

    def result(self):
        if self.vul_source_signature:
            return True, self.vul_stack[::-1], self.vul_source_signature, self.vul_method_signature
        return False, None, None, None