from lilya.contrib.mail.dependencies import _resolve_mailer as resolve_mailer

from esmerald.injector import Inject

Mail = Inject(resolve_mailer)

__all__ = ["Mail"]
