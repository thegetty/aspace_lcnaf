import lcnaf
import sys
import logging

def run(func,env,filename,agentType):
	logFile = './log/%s_%s_%s.log' % (func,agentType,env)
	logging.basicConfig(filename=logFile,
						format='%(levelname)s %(asctime)s   %(message)s',
						level=logging.INFO
						)
	if func == 'create':
		lcnaf.create(env,filename,agentType)
	if func == 'merge':
		lcnaf.merge(env,filename,agentType)

if __name__ == '__main__':
	run(*sys.argv[1:])