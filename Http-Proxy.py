""" //////////////////////////////////////////////////
                HTTP PROXY IMPLEMENTATION
    ////////////////////////////////////////////////// """

""" ////////////////////
           NOTES
    //////////////////// """

""" Built Using Pycharm """
""" Tested Using POSTMAN """
""" Test cases file runs fine and POSTMAN get the response on any request you want """
""" Errors 400 & 501 are handled and tested on POSTMAN """
""" HEAD, POST, PUT, DELETE Set to be Not Implemented and return error 501, anything else return error 400 bad Request """
""" Cache is handled for Pre-Visited Websites """
""" Threading are handled on Multi-Users requests """
""" ///// CODE SKELETON IS PROVIDED BY COMPUTER NETWORKS COURSE TEACHING ASSISTANTS ///// """

""" TOTAL USED FUNCTIONS = 15 """
""" TOTAL UNUSED FUNCTIONS = 2 """

""" ///////////////////////////////////////////////////////////////////////////////////////////// """
""" ///////////////////////////////////////////////////////////////////////////////////////////// """

""" IMPORTS & GLOBAL VARIABLES """
import sys
import os
import enum
import re
import socket
from _thread import *
import threading

client_addr = ("127.0.0.1", 9877)


class HttpRequestInfo(object):

    def __init__(self, client_info, method: str, requested_host: str,
                 requested_port: int,
                 requested_path: str,
                 headers: list):
        self.method = method
        self.client_address_info = client_info
        self.requested_host = requested_host
        self.requested_port = requested_port
        self.requested_path = requested_path
        # Headers will be represented as a list of lists
        # for example ["Host", "www.google.com"]
        # if you get a header as:
        # "Host: www.google.com:80"
        # convert it to ["Host", "www.google.com"] note that the
        # port is removed (because it goes into the request_port variable)
        self.headers = headers

    def to_http_string(self):
        Http = '';
        Http = Http + self.method + ' '

        if self.requested_path == '':
            Http = Http + self.requested_path
        else:
            Http = Http + self.requested_path

        Http = Http + ' ' + 'HTTP/1.0' + '\r\n'
        for Part in self.headers:
            Http = Http + Part[0] + ': ' + Part[1] + '\r\n'

        Http = Http + '\r\n'
        return Http

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
        return bytes(http_string, "UTF-8")

    def display(self):
        print(f"Client:", self.client_address_info)
        print(f"Method:", self.method)
        print(f"Host:", self.requested_host)
        print(f"Port:", self.requested_port)
        stringified = [": ".join([k, v]) for (k, v) in self.headers]
        print("Headers:\n", "\n".join(stringified))


class HttpErrorResponse(object):

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def to_http_string(self):
        Http_Version = "HTTP/1.0"
        error = Http_Version + " " + str(self.code) + " " + self.message + "\r\n\r\n"
        return error

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
        return bytes(http_string, "UTF-8")

    def display(self):
        print(self.to_http_string())


class HttpRequestState(enum.Enum):
    INVALID_INPUT = 0
    NOT_SUPPORTED = 1
    GOOD = 2
    PLACEHOLDER = -1


def entry_point(proxy_port_number):
    # Declare Empty List For Cache
    Cached = dict()
    print("=" * 20)
    print("Entry Point")
    print("=" * 20)
    s = setup_sockets(proxy_port_number)
    do_socket_logic(s, Cached)

    # Threading
    for i in range(0,15):
        try:
            _thread.start_new_thread(do_socket_logic, (s, Cached))
        except:
            print("No Threads")
    while True:
        pass


def do_socket_logic(s, Cached):
    while True:
        client, address = s.accept()
        Input = client.recv(1024)
        New = Input.decode("utf-8")
        array = http_request_pipeline(address, New)
        if (array[0] == HttpRequestState.GOOD):
            Parsed = array[1]
            Parsed.display()
            Parsed.requested_host = Parsed.requested_host.split("http:")[1]
            Parsed.headers.pop()

            str = Parsed.method + Parsed.requested_path + Parsed.requested_host
            if str in Cached:
                print("/" * 100)
                print("Entered Cache")
                print("/" * 100)
                while True:
                    Response = Cached[str]
                    client.send(Response)
                    client.close()
                    break
            else:
                NEW = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                NEW.connect((Parsed.requested_host, Parsed.requested_port))
                SEND = Parsed.to_byte_array(Parsed.to_http_string())
                NEW.send(SEND)
                list = b""
                while True:
                    Response = NEW.recv(1024)
                    client.send(Response)
                    list += Response
                    if len(Response) <= 0:
                        Cached[str] = list
                        NEW.close()
                        client.close()
                        break
        # Error Handling
        elif array[0] == HttpRequestState.NOT_SUPPORTED:
            error = HttpErrorResponse(501, "Not Implemented")
            Out = error.to_byte_array(error.to_http_string())
            client.send(Out)
        # Error Handling
        elif array[0] == HttpRequestState.INVALID_INPUT:
            error = HttpErrorResponse(400, "Bad Request")
            Out = error.to_byte_array(error.to_http_string())
            client.send(Out)
    pass


def setup_sockets(proxy_port_number):
    print("Starting HTTP proxy on port: ", proxy_port_number)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", proxy_port_number))
    s.listen(15)
    return s


def http_request_pipeline(source_addr, http_raw_data):
    print("=" * 20)
    print("Entering Pipeline")
    print("=" * 20)
    State = check_http_request_validity(http_raw_data)
    Parsed = parse_http_request(client_addr, http_raw_data)
    array = [State, Parsed]
    return array


def parse_http_request(source_addr, http_raw_data):
    print("=" * 20)
    print("Parsing Your Input")
    print("=" * 20)
    http_raw_data = http_raw_data.replace("\r\n\r\n", '')
    In = http_raw_data.split("\r\n")
    #print(In)

    Method = In[0].split(' ')[0]
    #print(Method)
    Path = In[0].split(' ')[1]
    HTTP_Version = In[0].split(' ')[2]

    if Path == "/" and In[1] == '':
        print("Invalid Input")
    elif Path[0] == "/" and In[1] == '':
        hostname = In[0].split(' ')[0]
        header_value = In[0].split(' ')[1]
        print("Relative Path")
        #print("Method: " + Method)
        #print("Path: " + Path)
        #print("HTTP Version: " + HTTP_Version)
        #print("Header: " + hostname.replace(':', ''))
        #print("Header Name: " + header_value)
        HeadersCustom = check_extra_header(http_raw_data)
        HeadersCustom.append([hostname.replace(':', ''), header_value])
        ret = HttpRequestInfo(source_addr, Method, header_value, 80, Path, HeadersCustom)
        return ret
        pass
    elif Path[0] == "/" and In[1] != '':
        hostname = In[1].split(' ')[0]
        header_value = In[1].split(' ')[1]
        print("Relative Path")
        #print("Method: " + Method)
        #print("Path: " + Path)
        #print("HTTP Version: " + HTTP_Version)
        #print("Header: " + hostname.replace(':', ''))
        #print("Header Name: " + header_value)
        HeadersCustom = check_extra_header(http_raw_data)
        HeadersCustom.append([hostname.replace(':', ''), header_value])
        ret = HttpRequestInfo(source_addr, Method, header_value, 80, Path, HeadersCustom)
        return ret
        pass
    else:
        print("Normal Path")
        return sanitize_http_request(http_raw_data)


def check_http_request_validity(http_raw_data) -> HttpRequestState:
    print("=" * 20)
    print("Validating Your Input")
    print("=" * 20)

    http_raw_data = http_raw_data.replace('\r\n\r\n', '')
    command = http_raw_data.split('\r\n')
    z = (len(command))

    #print(z)
    rex = re.compile("[a-z]{3} [\a-z]{1,} [\a-z]{3,}")
    rex2 = re.compile("[\a-z]{4,}: [\a-z]{3,}")
    meth = command[0].split(' ')[0]
    host_test = command[0].split(' ')[1]
    if rex.match(command[0].lower()) and method_checker(meth) == 1 and z < 2:
        print("Valid format")
        x = command[0].split(' ')[0]
        y = command[0].split(' ')[1]
        if y == "/":
            print("Invalid Input")
            return HttpRequestState.INVALID_INPUT
        else:
            return HttpRequestState.GOOD
        pass
    elif rex.match(command[0].lower()) and method_checker(meth) == 1:
        print("Valid format")
        return HttpRequestState.GOOD
        pass
    elif rex.match(command[0].lower()) and rex2.match(command[1].lower()) and method_checker(meth) == 1:
        print("Valid format")
        return HttpRequestState.GOOD
        pass
    else:
        print("Invalid format")
        z = command[0].split(' ')[2]
        versions = ["HTTP/1.0", "HTTP/1.1", "HTTP/2.0"]
        if len(command) == 1 and host_test.startswith('/'):
            return HttpRequestState.INVALID_INPUT
        elif method_checker(meth) == 0 and command[1].find(":") == -1:
            return HttpRequestState.INVALID_INPUT
        elif method_checker(meth) == 0 and z not in versions:
            return HttpRequestState.INVALID_INPUT
        elif method_checker(meth) == 0:
            return HttpRequestState.NOT_SUPPORTED
        elif method_checker(meth) == 2:
            return HttpRequestState.INVALID_INPUT
        pass

    pass


def sanitize_http_request(request_info: HttpRequestInfo):
    print("=" * 20)
    print("Sanitizing HTTP Request")
    print("=" * 20)

    request_info = request_info.replace('\r\n\r\n', '')
    Part = request_info.split('\r\n')
    Method = Part[0].split(' ')[0]
    Path = Part[0].split(' ')[1]
    #HTTP_Version = Part[0].split(' ')[2]
    # print("Method: " + Method)
    # print("HTTP Version: " + HTTP_Version)

    cut = Path.split("/")
    New = "/" + cut[-1]
    # print("New Path: " + New)
    HeadersCustom = check_extra_header(request_info)
    x = len(Path)
    if Path[x - 1] == "/":
        Path = Path.replace(Path[x - 1], '')
        # print("Done")
    # print("Host: " + Path)
    HeadersCustom.append(['Host', Path])
    # print(HeadersCustom)
    ret = HttpRequestInfo(client_addr, Method, Path, 80, New, HeadersCustom)
    return ret


def check_extra_header(command):
    command = command.replace('\r\n\r\n', '')
    Part = command.split('\r\n')
    length = len(Part)
    HeadersCustom = []
    i = 2
    rex = re.compile("[\a-z]{2,}: [\a-z]{3,}")
    while i < length:
        if rex.match(Part[i].lower()):
            Header = Part[i].split(' ')[0]
            Header_Name = Part[i].split(' ')[1]
            New = [Header.replace(':', ''), Header_Name]
            #print(New)
            HeadersCustom.append(New)
        i += 1

    return HeadersCustom


def method_checker(method):
    if method == "GET":
        return 1
    elif method == "DELETE" or method == "PUT" or method == "POST" or method == "HEAD":
        return 0
    else:
        return 2


#######################################
# Leave the code below as is.
#######################################


def get_arg(param_index, default=None):
    try:
        return sys.argv[param_index]
    except IndexError as e:
        if default:
            return default
        else:
            print(e)
            print(
                f"[FATAL] The comand-line argument #[{param_index}] is missing")
            exit(-1)  # Program execution failed.


def check_file_name():
    script_name = os.path.basename(__file__)
    import re
    matches = re.findall(r"(\d{4}_){,2}lab2\.py", script_name)
    if not matches:
        print(f"[WARN] File name is invalid [{script_name}]")
    else:
        print(f"[LOG] File name is correct.")


def main():
    print("=" * 27)
    #print(f"[LOG] Printing command line arguments [{', '.join(sys.argv)}]")
    check_file_name()
    print("=" * 27)
    print("="*42)
    print("----- Kindly Use Postman For Testing -----")
    print("="*42)

    # This argument is optional, defaults to 18888
    proxy_port_number = get_arg(1, 18888)
    entry_point(proxy_port_number)


if __name__ == "__main__":
    main()
