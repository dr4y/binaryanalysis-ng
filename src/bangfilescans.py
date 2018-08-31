#!/usr/bin/python3

## Binary Analysis Next Generation (BANG!)
##
## This file is part of BANG.
##
## BANG is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License,
## version 3, as published by the Free Software Foundation.
##
## BANG is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public
## License, version 3, along with BANG. If not,
## see <http://www.gnu.org/licenses/>
##
## Copyright 2018 - Armijn Hemel
## Licensed under the terms of the GNU Affero General Public
## License version 3
## SPDX-License-Identifier: AGPL-3.0-only

## This file has several methods for scanning files
## Each file has the following parameters:
##
## * filename (pathlib.Path object)
## * hashes (as a dict)
## * database connection object (PostgreSQL)
## * database cursor objec tPostgreSQL)

def knownfileNSRL(filename, hashresults, dbconn, dbcursor):
    '''A method to search a hash of a file in the NSRL database
    '''
    ## results is (for now) a list
    results = []

    if dbconn == None:
        return results

    ## first grab a *possible* filename from the NSRL database using
    ## the SHA1 of the file. At the moment just one *possible* filename
    ## is recorded in the database.
    dbcursor.execute("SELECT filename FROM nsrl_hash WHERE sha1=%s", (hashresults['sha1'],))
    res = dbcursor.fetchall()
    dbconn.commit()

    if len(res) == 0:
        return results

    manufacturercache = {}

    ## get more results
    for i in res:
        dbcursor.execute("SELECT n.productname, n.productversion, n.applicationtype FROM nsrl_product n, nsrl_entry m WHERE n.productcode = m.productcode AND m.sha1=%s;", (hashresults['sha1'],))
        productres = dbcursor.fetchall()
        dbconn.commit()
        for p in productres:
            ## first create a result object
            dbres = {}
            (productname, productversion, applicationtype, manufacturercode) = p
            if manufacturercode in manufacturercache:
                manufacturer = manufacturercache[manufacturercode]
            else:
                dbcursor.execute("SELECT manufacturername FROM nsrl_manufacturer WHERE manufacturercode=%s", (manufacturercode,))
                manufacturerres = dbcursor.fetchone()
                if manufacturerres == None:
                     ## this shouldn't happen
                     dbconn.commit()
                     return results
                manufacturer = manufacturerres[0]
                manufacturercache[manufacturercode] = manufacturer
                dbconn.commit()
            dbres['productname'] = productname
            dbres['productversion'] = productversion
            dbres['applicationtype'] = applicationtype
            dbres['manufacturer'] = manufacturer
            ## add the result to the final list of results
            results.append(dbres)

    return results