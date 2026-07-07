from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'
    verbose_name = 'Alert Scheduler'

    def ready(self):
        """
        Start the APScheduler background scheduler when Django is ready.

        Guard logic:
        - In development (`runserver`): Django's auto-reloader starts the
          process twice (parent + child). `RUN_MAIN=true` is set only on
          the *child* (the real server process), so we start the scheduler
          there to avoid double registration.
        - In production (Gunicorn / Uvicorn / WSGI): `RUN_MAIN` is never
          set, so we always start the scheduler.  If you run multiple
          Gunicorn workers, set AGRIFLOW_SCHEDULER_ENABLED=true only on
          the *first* worker (or use a beat process) to avoid races.
        """
        import os
        run_main = os.environ.get('RUN_MAIN')   # set by Django's reloader

        # In dev, only run in the child process (run_main == 'true').
        # In production run_main is None/empty → always start.
        if run_main == 'false':
            # This is the reloader parent process – skip.
            return

        from scheduler.jobs import start_scheduler
        start_scheduler()
