from lxml.html import parse, open_in_browser

url = 'http://neubloc.omnis.pl'
page = parse(url)

page.make_links_absolute(url)
form = page.forms[0]
form.inputs['name'].value = 'mrim'
form.inputs['pass'].value = '#'
res = form.submit()
res_page = parse(res)
res_page.make_links_absolute(res_page.geturl())
open_in_browser(res_page)
