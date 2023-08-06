class InvalidGrantException(Exception):
    pass


class ClientError(Exception):
    pass


class ServerError(Exception):
    pass


class HTTP400BadRequest(ClientError):
    pass


class HTTP401Unauthorized(ClientError):
    pass


class HTTP402PaymentRequired(ClientError):
    pass


class HTTP403Forbidden(ClientError):
    pass


class HTTP404NotFound(ClientError):
    pass


class HTTP405MethodNotAllowed(ClientError):
    pass


class HTTP406NotAcceptable(ClientError):
    pass


class HTTP407TemporaryRedirect(ClientError):
    pass


class HTTP408RequestTimeout(ClientError):
    pass


class HTTP409Conflict(ClientError):
    pass


class HTTP410Gone(ClientError):
    pass


class HTTP411LengthRequired(ClientError):
    pass


class HTTP412PreconditionFailed(ClientError):
    pass


class HTTP413PayloadTooLarge(ClientError):
    pass


class HTTP414UriTooLong(ClientError):
    pass


class HTTP415UnsupportedMediaType(ClientError):
    pass


class HTTP416RangeNotSatisfiable(ClientError):
    pass


class HTTP417ExpectationFailed(ClientError):
    pass


class HTTP418ImATeapot(ClientError):
    pass


class HTTP421MisdirectedRequest(ClientError):
    pass


class HTTP422UnprocessableEntity(ClientError):
    pass


class HTTP423Locked(ClientError):
    pass


class HTTP424FailedDependency(ClientError):
    pass


class HTTP425TooEarly(ClientError):
    pass


class HTTP426UpgradeRequired(ClientError):
    pass


class HTTP428PreconditionRequired(ClientError):
    pass


class HTTP429TooManyRequests(ClientError):
    pass


class HTTP431RequestHeaderFieldsTooLarge(ClientError):
    pass


class HTTP451UnavailableForLegalReasons(ClientError):
    pass


class HTTP500InternalServerError(ServerError):
    pass


class HTTP501NotImplemented(ServerError):
    pass


class HTTP502BadGateway(ServerError):
    pass


class HTTP503ServiceUnavailable(ServerError):
    pass


class HTTP504GatewayTimeout(ServerError):
    pass


class HTTP505HttpVersionNotSupported(ServerError):
    pass


class HTTP506VariantAlsoNegotiates(ServerError):
    pass


class HTTP507InsufficientStorage(ServerError):
    pass


class HTTP508LoopDetected(ServerError):
    pass


class HTTP510NotExtended(ServerError):
    pass


class HTTP511NetworkAuthenticationRequired(ServerError):
    pass


def raise_exception(status_code: int):
    if status_code // 100 != 4 and status_code // 100 != 5:
        return
    if status_code == 400:
        raise HTTP400BadRequest("The server couldn't resolve the request because of invalid syntax.")

    if status_code == 401:
        raise HTTP401Unauthorized("The client should authenticate itself to get the requested response.")

    if status_code == 402:
        raise HTTP402PaymentRequired(
            "Reserved for future use. The aim is to recommend the user to perform "
            "payment steps on digital payment systems."
        )

    if status_code == 403:
        raise HTTP403Forbidden(
            "The client does not have the access right for the content. "
            "Unlike 401, the identity of the client is known by the server."
        )

    if status_code == 404:
        raise HTTP404NotFound("The server can not find the requested resource.")

    if status_code == 405:
        raise HTTP405MethodNotAllowed(
            "The request method is known by the server but it is not supported by the target resource.")

    if status_code == 406:
        raise HTTP406NotAcceptable(
            "This response is sent when the web server, after performing server-driven content negotiation, "
            "doesn't find any content that conforms to the criteria given by the user agent."
        )

    if status_code == 407:
        raise HTTP407TemporaryRedirect(
            "Similar to 401 response but this time authentication is needed to be done by proxy.")

    if status_code == 408:
        raise HTTP408RequestTimeout(
            "This indicates the server didn't receive a complete request message within "
            "the server’s allotted timeout period."
        )

    if status_code == 409:
        raise HTTP409Conflict("This response is sent when a request conflicts with the current state of the server.")

    if status_code == 410:
        raise HTTP410Gone(
            "This is sent when the requested content has been "
            "permanently deleted from server, with no forwarding address."
        )

    if status_code == 411:
        raise HTTP411LengthRequired(
            "Server rejected the request because the Content-Length header field is not defined in the request.")

    if status_code == 412:
        raise HTTP412PreconditionFailed("Pre-defined preconditions in the header part didn't meet by the server.")

    if status_code == 413:
        raise HTTP413PayloadTooLarge("Request entity is larger than the limits defined by the server.")

    if status_code == 414:
        raise HTTP414UriTooLong("The URI requested by the client is longer than the server is willing to interpret.")

    if status_code == 415:
        raise HTTP415UnsupportedMediaType("The media format of the data is not supported.")

    if status_code == 416:
        raise HTTP416RangeNotSatisfiable(
            "The range specified by the Range header field in the request cannot be fulfilled.")

    if status_code == 417:
        raise HTTP417ExpectationFailed(
            "It means the expectation indicated by the Expect request header field cannot be met by server.")

    if status_code == 418:
        raise HTTP418ImATeapot(
            "This HTTP status is used as an Easter egg in some websites, including Google.com. "
            "The server refuses the attempt to brew coffee with a teapot."
        )

    if status_code == 421:
        raise HTTP421MisdirectedRequest("Request was directed to a server that is not able to create a response.")

    if status_code == 422:
        raise HTTP422UnprocessableEntity(
            "The request was well-formed but was unable to be followed due to semantic errors.")

    if status_code == 423:
        raise HTTP423Locked("The resource that is being accessed is locked for security reasons.")

    if status_code == 424:
        raise HTTP424FailedDependency("Request is failed due to failure of a previous request.")

    if status_code == 425:
        raise HTTP425TooEarly(
            "Indicates that the server is unwilling to risk processing a request that might be replayed.")

    if status_code == 426:
        raise HTTP426UpgradeRequired(
            "The server refuses to perform the request using the current protocol but might be willing to do so "
            "after the client upgrades to a different protocol."
        )

    if status_code == 428:
        raise HTTP428PreconditionRequired("The origin server requires the request to be conditional.")

    if status_code == 429:
        raise HTTP429TooManyRequests("The client has sent too many requests in a given time.")

    if status_code == 431:
        raise HTTP431RequestHeaderFieldsTooLarge(
            "Indicates that the header fields of the request are too large to handle.")

    if status_code == 451:
        raise HTTP451UnavailableForLegalReasons(
            "The user agent requested a resource that cannot legally be provided, "
            "such as a web page censored by a government."
        )

    if status_code == 500:
        raise HTTP500InternalServerError(
            "Server has faced an erroneous situation and it does not know how to handle that.")

    if status_code == 501:
        raise HTTP501NotImplemented("The request method is not supported by the server.")

    if status_code == 502:
        raise HTTP502BadGateway(
            "This error response indicates that the server, "
            "while working as a gateway to get a response needed to handle the request, "
            "got an invalid response during the flow."
        )

    if status_code == 503:
        raise HTTP503ServiceUnavailable(
            "The server is not ready to handle the request yet. "
            "It can be because the server is down for maintenance or it is overloaded."
        )

    if status_code == 504:
        raise HTTP504GatewayTimeout("The server is acting like a gateway and it cannot get a response in a given time.")

    if status_code == 505:
        raise HTTP505HttpVersionNotSupported(
            "The HTTP version used in the request is not supported by that specific server.")

    if status_code == 506:
        raise HTTP506VariantAlsoNegotiates(
            "the chosen variant resource is configured to engage in transparent content negotiation itself, "
            "and is therefore not a proper end point in the negotiation process."
        )

    if status_code == 507:
        raise HTTP507InsufficientStorage(
            "The method could not be performed on the resource because the server is unable to store the "
            "representation needed to successfully complete the request."
        )

    if status_code == 508:
        raise HTTP508LoopDetected("The server detected an infinite loop while processing the request.")

    if status_code == 510:
        raise HTTP510NotExtended("Further extensions to the request are required for the server to fulfill it.")

    if status_code == 511:
        raise HTTP511NetworkAuthenticationRequired("The client needs to authenticate itself to gain network access.")
