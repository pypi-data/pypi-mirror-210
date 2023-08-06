'''
Build request for quering LUCAS dataset.
'''
from owslib import __version__ as owslib_version
from owslib.etree import etree
from owslib.fes import Or, And, PropertyIsEqualTo, BBox, PropertyIsNull, Not

from .exceptions import LucasRequestError, LucasOWSLibError

def check_owslib():
    """Check supported OWSLib version.

    Raises LucasRequestError on unsupported OWSLib version.
    """
    owslib_min = 0.22
    owslib_max = 0.26
    owslib_ver = float('.'.join(owslib_version.split('.')[:2]))
    if owslib_ver > owslib_min and owslib_ver < owslib_max:
        raise LucasOWSLibError(
            f"Unsupported OWSLib version: {owslib_version}. "
            f"Supported versions: <={owslib_min}, >={owslib_max}"
        )

class LucasRequest:
    """Define a request.
    """
    bbox = None
    operator = None
    propertyname = None
    literal = None
    logical = None
    years = None
    countries = None
    aoi_polygon = None
    st_aggregated = False
    group = None

    gh_workspace = 'lucas'
    gh_typename = 'lucas_points'
    gh_typename_st = 'lucas_st_points'

    @property
    def typename(self):
        typename = self.gh_typename_st if self.st_aggregated else self.gh_typename
        if self.group is not None:
            typename += f'_{self.group}'.lower()
        return f'{self.gh_workspace}:{typename}'

    def __setattr__(self, name, value):
        if name not in (
                'bbox',
                'operator',
                'propertyname',
                'literal',
                'logical',
                'years',
                'countries',
                'aoi_polygon',
                'group',
                'st_aggregated'):
            raise LucasRequestError(f"{name} not allowed")

        super().__setattr__(name, value)

    def _check_args(self):
        """Check for required arguments.

        Raise LucasRequestError if requirements are not defined.
        """
        if self.bbox is None and \
           self.aoi_polygon is None and \
           self.countries is None and \
           self.propertyname is None:
            raise LucasRequestError(
                "spatial filter (bbox, countries, aoi_polygon) or attribute filter (propertyname) must be defined."
            )
        if self.bbox is not None and self.aoi_polygon is not None:
            raise LucasRequestError("bbox and aoi_polygon are mutually exclusive.")
        if self.bbox is not None and self.countries is not None:
            raise LucasRequestError("bbox and countries are mutually exclusive.")
        if self.aoi_polygon is not None and self.countries is not None:
            raise LucasRequestError("aoi_polygon and countries are mutually exclusive.")
        # check supported OWSLib version
        check_owslib()

    def __build_years_property(self, query=None):
        query_years = self.__build_years(query)
        if self.propertyname:
            return self.__build_property(
                self.propertyname.lower(), self.literal, self.operator, self.logical,
                query_years
            )
        return query_years

    def __build_years(self, query=None):
        filter_years = []
        if self.years is not None:
            for value in self.years:
                if self.st_aggregated:
                    filter_years.append(
                        Not([PropertyIsNull(propertyname=f'survey_date_{str(value)}')])
                    )
                else:
                    filter_years.append(
                        PropertyIsEqualTo(propertyname='survey_year',
                                          literal=str(value))
                    )

        if not filter_years:
            return query
        elif len(filter_years) > 1:
            if query:
                return And([
                    query,
                    Or(filter_years)
                ])
            else:
                return Or(filter_years)
        else:
            if query:
                return And([
                    query,
                    filter_years[0]
                ])
            else:
                return filter_years[0]

        return None

    def __build_property(self, propertyname, literal, operator, logical, query=None):
        # check requirements
        if propertyname is None:
            raise LucasRequestError(
                "Property name is not defined"
            )
        if literal is None:
            raise LucasRequestError(
                "Literal property is not defined"
            )

        # collect list of literals
        if isinstance(literal, str):
            literal = [literal]
        elif isinstance(literal, list):
            literal = literal
        elif isinstance(literal, int):
            literal = [str(literal)]
        else:
            raise LucasRequestError(
                "Literal property must be provided as a string or a list."
            )

        # check if logical operator is required
        if isinstance(literal, list) and len(literal) > 1 and logical is None:
            raise LucasRequestError(
                "Logical property is not defined."
            )

        # get list of property filters
        filter_list = []
        for value in literal:
            if propertyname in ('point_id', 'nuts0', 'survey_count', 'survey_maxdist') or self.st_aggregated is False:
                filter_list.append(
                    operator(propertyname=propertyname, literal=value)
                )
            else:
                st_filter = []
                for year in ['_2006', '_2009', '_2012', '_2015', '_2018']:
                    st_filter.append(
                        operator(propertyname=propertyname + year, literal=value)
                    )
                filter_list.append(Or(st_filter))


        # get combined property filter
        if len(literal) > 1:
            filter_property = logical(filter_list)
        else:
            filter_property = filter_list[0]

        if query:
            return And([query, filter_property])

        return filter_property

    def build(self):
        """
        Return a request arguments (bbox, filter) for the getfeature() method.

        :return dict:
        """
        self._check_args()

        req = {
            'typename': self.typename
        }

        #
        # filter by bbox
        #
        if self.bbox is not None:
            bbox_query = BBox(self.bbox)
            filter_ = self.__build_years_property(bbox_query)

            # TODO: workaround for owslib bug
            tree = filter_.toXML()
            namespaces = {'gml311': 'http://www.opengis.net/gml'}
            envelopes = tree.findall('.//gml311:Envelope', namespaces)
            for envelope in envelopes:
                envelope.set('srsName', 'http://www.opengis.net/gml/srs/epsg.xml#3035')

            filter_xml = etree.tostring(tree).decode("utf-8")
            # TODO maybe change this in XML way as well
            filter_xml = filter_xml.replace('ows:BoundingBox', 'geom')

            req.update({'filter': filter_xml})

        #
        # filter by countries
        #
        if self.countries is not None:
            countries_query = self.__build_property(
                'nuts0', self.countries, PropertyIsEqualTo, Or
            )
            filter_ = self.__build_years_property(countries_query)

            req.update({
                'filter': etree.tostring(filter_.toXML()).decode("utf-8")
            })

        #
        # filter by polygon
        #
        if self.aoi_polygon is not None:
            filter_ = self.__build_years_property()
            # merge with year filter if defined
            if filter_ is not None:
                filter_xml = etree.tostring(filter_.toXML()).decode("utf-8")
                filter_xml = '<ogc:And xmlns:ogc="http://www.opengis.net/ogc">' + filter_xml + self.aoi_polygon + '</ogc:And>'
            else:
                filter_xml = self.aoi_polygon

            req.update({'filter': filter_xml})

        if self.bbox is None and \
           self.countries is None and \
           self.aoi_polygon is None and \
           self.propertyname is not None:
            filter_ = self.__build_property(
                self.propertyname, self.literal, self.operator, self.logical
            )

            req.update({
                'filter': etree.tostring(filter_.toXML()).decode("utf-8")
            })

        return req
