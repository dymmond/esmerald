from lilya.middleware.clickjacking import XFrameOptionsMiddleware as LilyaXFrameOptionsMiddleware

from esmerald.conf import settings


class XFrameOptionsMiddleware(LilyaXFrameOptionsMiddleware):

    def get_xframe_options(self) -> str:
        """
        Get the X-Frame-Options value from the settings.

        Returns:
            str: The X-Frame-Options value.
        """
        if getattr(settings, "x_frame_options", None) is not None:
            return settings.x_frame_options.upper()
        return "DENY"
