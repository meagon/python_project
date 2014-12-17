
class spider(object):

    global g_workers

    imgs = []

    def __init__(self, store_queue=None, parse_queue=None,
                 img_download_queue=None,
                 download_queue=None, limits=None, *args, **kwds):
        self.store_queue = store_queue
        self.parse_queue = parse_queue
        self.download_queue = download_queue
        self.img_download_queue = img_download_queue
        self.limits = limits

    @classmethod
    def add_img(kls, item):
        return kls.imgs.append(item)

    def img_count(self):
        return len(self.imgs)

    def workers(self):
        pass

    def run(self):
        while 1:
            inqueue = not self.store_queue.empty() and self.store_queue  \
                or ( not self.img_download_queue.empty() and self.img_download_queue ) \
                or ( not self.parse_queue.empty() and self.parse_queue) \
                or ( not self.download_queue.empty() and self.download_queue) \
                or None
            status = [i.working for i in g_workers]
            logger.info(" all threads status is : %r" % str(status))
            running = [i for i in g_workers if i.working is not None]

            logger.debug("working unit : %d " % len(running))
            logger.debug("store queue size : %r" % self.store_queue.qsize())
            logger.debug("img queue size: %r " %
                         self.img_download_queue.qsize())
            logger.debug("parse size :%r   " % self.parse_queue.qsize())

            if self.limits is not None and self.img_count() >= self.limits:
                kill_all()

            if inqueue is not None:
                self.task = inqueue.get()
                logger.info("asking for a new task %s " % self.task[0])
                self._sched()
            else:
                if len(running) < 6:
                    logger.info("running task less than 6 and ")
                    for g in running:
                        logger.info(
                            "live task doing job :%r url: %r" % (g.working, g.page))
                if len(running) < 6:
                    logger.info("less than six spiders has no work ?")
                g = gevent.getcurrent()
                g.working = None
                logger.warning(
                    "queues  empty and working size: %d" % len(running))
                gevent.sleep(0.3)
                continue

            self.task = inqueue.get()
            logger.info("asking for a new task %s " % self.task[0])
            self._sched()

    def _setup(self, tasks, inqueue):
        """ task  = ( job ,i , func ,*args, **kwds, result = task ) """
        for task in tasks:
            inqueue.put(task)

    @staticmethod
    def parse(*args, **kwds):
        page = kwds.get("page")
        page.parsed = True
        try:
            logger.info("at parsing %r url deepth:%r" %
                        (page.url, page.deepth))
            if page.fill_html():
                page.find_all_child()
                return page
        except Exception as e:
            logger.exception(e)
            return page

    @staticmethod
    def download(*args, **kwds):
        global download_records
        logger.debug("at download...  ")
        page = kwds.get("page")
        try:
            page.download()
            logger.info("download status: %r  url: %r " %
                        (page.status_code, page.url))
        except Exception as exc:
            logger.exception(exc)
            time.sleep(100)

        download_records.add(page.url)
        return page

    @classmethod
    def store(kls, *args, **kwds):

        global img_download_counter
        page = kwds.get("page")
        logger.info("store page: %r  deepth :%r" % (page.url, page.deepth))
        try:
            page.store()
            kls.add_img(page.url)
            page = None

            return True, page
        except Exception as error:
            logger.exception(error)
        return False, page

    def queue_transform(self, job, page, *args, **kwds):

        global download_records

        page.out_queue = None

        img_download_queue, parse_queue, img_store_queue = "download", "parse", "store"
        download_queue = img_download_queue

        try:
            if page.is_img() and page.url not in download_records:
                page.out_queue = download_queue
                db.save("img_download", page.url)
            elif page.is_img() and page.url in download_records:
                page.out_queue = img_store_queue
            elif not page.is_empty() and not hasattr(page, 'parsed'):
                page.out_queue = parse_queue
            # elif not page.is_empty() and hasattr(page, 'parsed'):
            #    page.out_queue = download_queue
            elif not page.is_empty() and not page.is_img() and hasattr(page, "parsed"):
                logger.info("add page child into download_queue")
                page.out_queue = download_queue
                db_save("parse", page.url)
                page.find_all_child()
                for child in page.childs:
                    db_save("childs", child.url)
            return page

        except Exception as exc:
            logger.exception(exc)
            time.sleep(10)
        return page

    def _sched(self):
        ''' different queue  masterd through this schedu '''

        logger.info(" at sched ..")
        job, i, func, args, kwds, result = self.task

        g = gevent.getcurrent()
        g.working = job
        g.page = kwds.get("page") and kwds.get("page").url

        logger.info("got job %r %r  page url = %r" %
                    (job, func, kwds["page"].url))
        try:
            status, page = (True, func(*args, **kwds))
        except Exception as e:
            result = (False, e)
            logger.exception(e)
            return

        if not page:
            return

        current_job, current_page = job, page

        if current_job == "store":
            return
        try:
            page = self.queue_transform(job=current_job, page=page)
            next_step = page.out_queue
        except Exception as e:
            logger.exception(e)
        try:
            logger.info("at sched .. current_job:  %r  next_job:  %r with page: %r"
                        % (current_job, next_step, page.url)
                        )

            if next_step == "store":
                try:
                    task = (
                        "store", None, self.store, (),  {"page": page}, result)
                    self.store_queue.put(task)
                    del task
                except Exception, e:
                    logger.exception("exception : %s " % (sys.exc_info()[1]))
            elif next_step == "parse":
                logger.debug(
                    "generate  next task %s to queue   %r" % (next_step, page.url))
                try:
                    task = (
                        "parse", None, self.parse, (),  {"page": page}, result)
                    self.parse_queue.put(task)
                    del task
                except Exception, e:
                    logger.exception(e)
            elif next_step == "download":
                logger.info("will add to download queue: %r" % page.childs)
                for child_page in page.childs:
                    if isinstance(child_page, Page):
                        task = (
                            "download", None, self.download, (), {"page": child_page}, result)
                        if child_page.is_img():
                            self.img_download_queue.put(task)
                        else:
                            self.download_queue.put(task)
            else:
                logger.debug(
                    "unknow next_step %r current_page : %r " % (next_step, current_page.url))
        except Exception as e:
            logger.exception(e)
        return
