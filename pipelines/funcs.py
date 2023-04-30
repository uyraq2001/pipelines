def domain_of_url(url):
    return url.split(".")[-1].split("/")[0]

funcs = {domain_of_url:1}