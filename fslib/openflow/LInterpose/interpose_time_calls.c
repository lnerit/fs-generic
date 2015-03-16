#define _GNU_SOURCE

#include <sys/types.h>
#include <sys/stat.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>

typedef int (*openX_proto)(char const *, int, ...);
typedef float (*timeX_proto)(time_t);
typedef float (*timeX_proto_fs)();

static openX_proto next_open = NULL;
static openX_proto next_open64 = NULL;

static timeX_proto next_time = NULL;
static timeX_proto_fs next_time_fs = NULL;

void __attribute__((constructor)) fsLib_init(void)
{
    fprintf(stderr, "%s", "Interpose_FSLib_init()\n");
    next_open = dlsym(RTLD_NEXT, "open");
    next_open64 = dlsym(RTLD_NEXT, "open64");
    next_time = dlsym(RTLD_NEXT,"ctime");
    next_time_fs = dlsym(RTLD_NEXT,"time");

    exec_pycode("print 'Hello fs time patch'");
}

void __attribute__((destructor)) fsLib_fini(void)
{
    fprintf(stderr, "%s", "Interpose_FSLib_end()\n");
}

static float timeX(timeX_proto func, time_t o)
{
    return func(o);
}

static float timeFS(timeX_proto_fs func)
{
    // return func(o);
    // return time from FakePoxTime
    exec_pycode("print 'Calling FakePoxTime Class'");
    char *code;
    float Timer = 0.1;
    sprintf(&code,"test \
        class FakePoxTimer(object): \
            timerid = 0 \
            def __init__ (self, timeToWake, callback, absoluteTime = False, recurring = False, args = (), kw = {}, scheduler = None, started = True, selfStoppable = True): \
                if absoluteTime and recurring: \
                    raise RuntimeError('Can't have a recurring timer for an absolute time!') \
                if absoluteTime: \
                    raise RuntimeError('Can't have an absolute time in FakePoxTimer') \
                self._self_stoppable = selfStoppable \
                self._timeToWake = timeToWake \
                self.id = 'poxtimer{}'.format(FakePoxTimer.timerid) \
                FakePoxTimer.timerid += 1 \
                self._recurring = recurring \
                self._callback = callback \
                self._args = args \
                self._kw = kw \
                get_logger().debug('Setting fake pox timer callback {} {}'.format(self._timeToWake, self._callback)) \
                fscore().after(self._timeToWake, self.id, self.docallback, None) \
            def cancel(self): \
                get_logger().debug('Attempting to cancel fake POX timer {}'.format(self.id)) \
                fscore().cancel(self.id) \
            def docallback(self, *args): \
                get_logger().debug('In fake pox timer callback {} {}'.format(self._timeToWake, self._callback)) \
                rv = self._callback(*self._args, **self._kw) \
                if rv and self._recurring: \
                    fscore().after(self._timeToWake, self.id, self.docallback, None) \
        # for now works only for pox \
        import pox.lib.recoco as recoco \
        setattr(recoco, 'Timer', FakePoxTimer) \
        return Timer\
    ");
    exec_pycode(code);
    
    PyObject *main_module, *expression, *global_dict;
    main_module = PyImport_AddModule("FakePoxTimer()");
    global_dict = PyModule_GetDict(main_module);
    expression = PyDict_GetItemString(global_dict, "Timer");
    
    return Timer;
}

void exec_pycode(const char* code)
{
    Py_Initialize();
    PyRun_SimpleString(code);
    Py_Finalize();
}

float timeCall(time_t m)
{
    fprintf(stderr, "time()\n");
    fflush(stderr);
    float ret = timeX(next_time, m);
    return ret;
}

float timeCallFS()
{
    fprintf(stderr, "fs_time()\n");
    fflush(stderr);
    float ret = timeFS(next_time_fs);
    return ret;
}

static int openX(openX_proto func, char const *pathname, int flags, va_list ap)
{
    if (flags & O_RDWR) {
        flags &= ~O_RDWR;
        flags |= O_RDONLY;
    } else if (flags & O_WRONLY) {
        flags &= ~O_WRONLY;
    }
    return func(pathname, flags, va_arg(ap, mode_t));
}

int open(char const *pathname, int flags, ...)
{
    fprintf(stderr, "open()\n");
    fflush(stderr);
    va_list ap;
    va_start(ap, flags);
    int ret = openX(next_open, pathname, flags, ap);
    va_end(ap);
    return ret;
}

int open64(char const *pathname, int flags, ...)
{
    fprintf(stderr, "open64()\n");
    fflush(stderr);
    va_list ap;
    va_start(ap, flags);
    int ret = openX(next_open64, pathname, flags, ap);
    va_end(ap);
    return ret;
}
