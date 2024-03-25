### Important note

In the examples you could see sometimes the `LilyaMiddleware` being used and in other you didn't. The reason behind
is very simple and also explained in the [middleware section](../../middleware/middleware.md#important).

If you need to specify parameters in your middleware then you will need to wrap it in a `lilya.middleware.DefineMiddleware`
object to do it so.

If no parameters are needed, then you can simply pass the middleware class directly and Esmerald will take care of the
rest.
