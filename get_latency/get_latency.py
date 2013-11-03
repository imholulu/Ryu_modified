import ping
import time
from threading import Thread
from SimpleXMLRPCServer import SimpleXMLRPCServer

class PingTask(object):
	def __init__(self, hostname, count=3, timeout=1000, packet_size=55):
		self.hostname = hostname
		self.count = count
		self.timeout = timeout
		self.latency = 0
		self.packet_size = packet_size
		self.p = ping.Ping(self.hostname, self.timeout, self.packet_size)
	def doPing(self):
		self.p.init()
		self.p.run(self.count)
		self.latency = self.p.getAverageDelay()
	def printLatency(self):
		print "Host:%s, delay:%f" % (self.hostname, self.latency)

class LatencyProxy:
	def __init__(self, host_task_dict):
		self.host_task_dict = host_task_dict
	def getLatency(self):
		#return self.host_task_dict
		re = dict()
		for host in self.host_task_dict.keys():
			re[host] = self.host_task_dict[host].latency
		return re


class TimerTask:
	def __init__(self, host_task_dict):
		self.host_task_dict = host_task_dict
	def schedule(self):
		for host in self.host_task_dict.keys():
			Thread(target=self.host_task_dict[host].doPing, args=()).start()
	def update(self):
		while True:
			#print "xxxx"
			#print host_task_dict
			self.schedule()
			for host in self.host_task_dict.keys():
				self.host_task_dict[host].printLatency()
			time.sleep(10)



if __name__ == '__main__':
	server = SimpleXMLRPCServer(("127.0.0.1",8000));
	host_task_dict = dict()
	proxy = LatencyProxy(host_task_dict)
	server.register_instance(proxy)
	with open('hosts.conf', 'r') as conf_file:
		for line in conf_file.readlines():
			host_task_dict[line.strip()] = PingTask(line.strip())
	timerTask = TimerTask(host_task_dict)
	Thread(target=timerTask.update,args=()).start()
	print "Server started"
	server.serve_forever()

	

