"""
Sub-class of main gevent.pywsgi.WSGIHandler.

Necessary in order to override some behaviour.
"""
import gevent
import gevent.pywsgi


class EDDNWSGIHandler(gevent.pywsgi.WSGIHandler):
    """Handles overriding request logging."""

    def format_request(self) -> str:
        """
        Format information about the request for logging.

        The default causes, e.g.:

        <client IP> - - [2022-03-12 16:44:39] "POST /upload/ HTTP/1.1" 400 399 0.000566

        and makes no attempt to handle reverse proxying where we know that
        X-Forwarded-For has been set by our reverse proxy.  So this will use
        that header if present to output the correct IP.

        Also, as we're pointing output at our logger, there is no need to
        include a timestamp in the output.

        This is why we're overriding *this* and not `handle_one_response()`,
        where we'd change self.client_address there instead.  This does,
        unfortunately, mean re-creating most of the super-class'es version
        of the function.

        Resulting output:

        2022-03-12 16:44:39.132 - INFO - pywsgi:1226: <client IP> - - "POST /upload/ HTTP/1.1" 400 399 0.000566
        """
        # Start with the same as the super-class would use...
        client_address = self.client_address[0] if isinstance(self.client_address, tuple) else self.client_address

        # ... but now over-ride it if the header is set.
        if self.environ.get("HTTP_X_FORWARDED_FOR"):
            client_address = self.environ["HTTP_X_FORWARDED_FOR"]

        length = self.response_length or '-'

        if self.time_finish:
            d = self.time_finish - self.time_start
            delta = f"{d:6f}"

        else:
            delta = '-'

        # This differs from the super-class version in not having a datestamp
        return f"{client_address or '-'} - - \"{self.requestline or '-'}\"" \
               f" {(self._orig_status or self.status or '000').split()[0]}" \
               f" {length} {delta}"
