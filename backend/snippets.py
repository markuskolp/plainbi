# -*- coding: utf-8 -*-

import urllib.parse
decodedurl = urllib.parse.unquote("http://localhost:3000/api/crud/1/DWH.config.tv_map_veranstaltungsreihe/(quell_nr:%2FMM%2FAccount%2FLogOn%3FReturnUrl%3D%252FMM%252FAccount%252FLogOn%253FReturnUrl%253D%25252fMM%25252fANL24%25252fOrderHistory:quelle:ga4)?v=1&pk=quell_nr%2Cquelle")
print(f"{decodedurl}")
