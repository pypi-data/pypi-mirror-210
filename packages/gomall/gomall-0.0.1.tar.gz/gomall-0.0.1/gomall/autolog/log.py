import os
import datetime


class AutoLog:
    def __init__(self, name='', path='./'):
        if not os.path.exists(path+'logs'):
            os.mkdir(path+'logs')
        if name == '':
            self._dir_name = path + 'logs' + '/log' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        else:
            self._dir_name = path + 'logs' + '/' + name
        os.mkdir(self._dir_name)
        os.mkdir(self._dir_name + '/constant')
        os.mkdir(self._dir_name + '/variable')
        self._constant = ['hyper']
        self._variable = ['metric']
        self._variables = {}
        self._need_best = {}
        self._best = {}
        self._start_time = 0

    def set_constant(self, *args):
        self._constant = []
        for item in args:
            self._constant.append(item)

    def set_variable(self, *args):
        self._variable = []
        for item in args:
            self._variable.append(item)

    def add_constant(self, *args):
        self._constant = []
        for item in args:
            self._constant.append(item)

    def add_variable(self, *args):
        self._variable = []
        for item in args:
            self._variable.append(item)

    def log_hyper(self, **kwargs):
        for k, v in kwargs.items():
            with open(self._dir_name+'/constant/hyper.log', 'a') as f:
                f.write('{"hyper": {"'+k+'": '+str(v)+'}}\n')

    def log_constant(self, constant, **kwargs):
        if constant not in self._constant:
            raise ValueError(constant+'不在constant列表内，请先使用add_constant(self, *args)进行添加')
        with open(self._dir_name + '/constant/' + constant + '.log', 'a') as f:
            for k, v in kwargs.items():
                f.write('{"'+constant+'": {"'+k+'": '+str(v)+'}}\n')

    def log_metric(self, step, **kwargs):
        if 'metric' not in self._variables:
            self._variables['metric'] = []
        with open(self._dir_name + '/variable/metric.log', 'a') as f:
            f.write('step: ' + str(step) + '    {"metric": ')
            comma = ''
            for k, v in kwargs.items():
                if k in self._variables['metric']:
                    pass
                else:
                    self._variables['metric'].append(k)
                f.write(comma+'{"'+k+'": '+str(v)+'}')
                comma = ', '
                if k in self._need_best:
                    if k not in self._best:
                        self._best[k] = (0, v)
                    else:
                        if self._need_best[k] == 'max':
                            if v > self._best[k][1]:
                                self._best[k] = (step, v)
                        else:
                            if v < self._best[k][1]:
                                self._best[k] = (step, v)
            f.write('}\n')

    def log_variable(self, variable, step, **kwargs):
        if variable not in self._variables:
            self._variables[variable] = []
        if variable not in self._variable:
            raise ValueError(variable+'不在variable列表内，请先使用add_variable(self, *args)进行添加')
        with open(self._dir_name + '/variable/'+variable+'.log', 'a') as f:
            f.write('step: ' + str(step) + '    {"'+variable+'": ')
            comma = ''
            for k, v in kwargs.items():
                if k in self._variables[variable]:
                    pass
                else:
                    self._variables[variable].append(k)
                f.write(comma+'{"'+k+'": '+str(v)+'}')
                comma = ', '
                if k in self._need_best:
                    if k not in self._best:
                        self._best[k] = (0, v)
                    else:
                        if self._need_best[k] == 'max':
                            if v > self._best[k][1]:
                                self._best[k] = (step, v)
                        else:
                            if v < self._best[k][1]:
                                self._best[k] = (step, v)
            f.write('}\n')

    def constant(self):
        return self._constant

    def variable(self):
        return self._variable

    def need_best(self, **kwargs):
        for k, v in kwargs.items():
            if v != 'max' and v != 'min':
                raise ValueError(v + '不是"max"或"min"的一种')
            self._need_best[k] = v

    def log_best(self, *args):
        for variable in args:
            with open(self._dir_name + '/variable/best_'+variable+'.log', 'a') as f:
                for item in self._variables[variable]:
                    if item in self._need_best:
                        f.write('step: ' + str(self._best[item][0]) + '    {"' + variable + '": ' + ' {"' + item + '": ' + str(self._best[item][1]) + '}}\n')

    def start(self):
        self._start_time = datetime.datetime.now()

    def end(self):
        if self._start_time == 0:
            raise AttributeError('请先用start函数开始计时')
        time = datetime.datetime.now() - self._start_time
        time = time.total_seconds()
        with open(self._dir_name + '/time.log', 'a') as f:
            f.write('{"time": '+str(time)+'}\n')

    def note(self, str):
        with open(self._dir_name + '/note.txt', 'a') as f:
            f.write(str)

