# -*- coding: utf-8 -*-
#   License: BSD-3-Clause
#   Author: LKouadio <etanoyau@gmail.com>
#   Created on Thu Sep 29 08:30:12 2022 

from __future__ import print_function , annotations
import os 
from warnings import warn 
import numpy as np 
import pandas as pd 

from .core import get_agso_properties 
from .geology import Geology
from .._typing import NDArray, DataFrame
from ..exceptions import NotFittedError 
from ..site import Profile 
from ..utils._dependency import import_optional_dependency 
from ..utils.box import data2Box 
from ..utils.coreutils import _is_readable, makeCoords 
from ..utils.funcutils import ( 
    _assert_all_types, 
    to_numeric_dtypes , 
    smart_strobj_recognition, 
    convert_value_in 
    )
from ..utils.geotools import get_random_thickness
from ..utils.validator import check_array 

class DSBoreholes :
    """
    Class deals with many boreholes dataset. 
    
    DSBoreholes works with the data set composed of multiple borehole data. 
    The data columns are the all attributes of the object and any 
    non-alphateic character is replaced by ``_``. For instance, a column name 
    ``layer thickness`` should have an attribute named ``layer_thickness``. 
    Each borehole (row) data become its own object which encompasses all 
    columns as attributes. To have full control of how data must be 
    retrieved, ``holeid`` parameter must be set. For instance, to retrieve 
    the borehole with ID equals to `bx02`, after fitting the class with 
    appropriate parameters, attibute `hole depth` ( if exist in the data) can  
    be retrieved as ``self.hole.bx02.hole_depth``. 
    
    By default if the projection is given as latitude/longitude 

    Parameters
    ------------
    area: str
       Name of area where the data collection is made. 
      
    holeid: str, optional 
       The name of column of the boreholes collections ID. Note that if 
       given, it should exist in the borehole datasets. 
      
    lon, lat: ArrayLike 1d /str  , optional 
       One dimensional arrays. `xlon` can be consider as the abscissa of   
       the landmark and `ylat` as ordinates array.  If `xlon` or `ylat` is  
       passed as string argument, `data` must be passed as `fit_params` 
       keyword arguments and the name of `xlon` and `y` must be a column 
       name of the `data`. 
       By default `xlon` and `ylat` are considered as `longitude` and 
       `latitude` when ``dms`` or ``ll`` coordinate system is passed.
       
    utm_zone: Optional, string
       zone number and 'S' or 'N' e.g. '55S'. Default to the centre point
       of coordinates points in the survey area. It should be a string (##N or ##S)
       in the form of number and North or South hemisphere, 10S or 03N
       
    projection: str, ['utm'|'dms'|'ll'] 
       The coordinate system in which the data points for the profile is collected. 
       If not given, the auto-detection will be triggered and find the  suitable 
       coordinate system. However, it is recommended to provide it for consistency. 
       Note that if `x` and `y` are composed of value less than 180 degrees 
       for longitude and 90 degrees for latitude, it should be considered as  
       longitude-latitude (``ll``) coordinates system. If `x` and `y` are 
       degree-minutes-second (``dms`` or ``dd:mm:ss``) data, they must be 
       specify as coordinate system in order to accept the non-numerical data 
       before transforming to ``ll``. If ``data`` is passed to the :meth:`.fit`
       method and ``dms`` is not specify, `x` and `y` values should be discarded.
       
    datum: string, default = 'WGS84'
       well known datum ex. WGS84, NAD27, NAD83, etc.

    epsg: Optional, int
       epsg number defining projection (
            see http://spatialreference.org/ref/ for moreinfo)
       Overrides utm_zone if both are provided. 

    encoding: str, default ='utf8'
       Default encoding for parsing data. Can also be ['utf-16-be'] for 
       reading bytes characters. 
       
    interp_coords: bool, default=False 
       Interpolate position coordinates.
      
    reference_ellipsoid: int, default=23 
       reference ellipsoids is derived from Peter H. Dana's website-
       http://www.utexas.edu/depts/grg/gcraft/notes/datum/elist.html
       Department of Geography, University of Texas at Austin
       Internet: pdana@mail.utexas.edu . Default is ``23`` constrained to 
       WGS84. 
       
    verbose: int, default=0 
       Output messages. 
      
    Attributes 
    ----------
    lon_, lat_: Arraylike, 
       longitude/latitude of coordinates arrays. 
       
    `hole.<holeid>.<data_column>`: :class:`~watex.utils.box.Boxspace` 
       Each borehole, commonly which ID correspond to  each row. Each row
       can be fetched as 'holeID'. If `holeid` is nt specified, the string 
       literal `hole+index of data` composed the borehole object. 
       
    Notes 
    ------
    When `data` is supplied and `lon` and `lat` are given by their names 
    existing in the dataframe columns, by default, the non-numerical 
    data are removed. However, if `y` and `x` are given in DD:MM:SS in 
    the dataframe, the coordinate system must explicitly set to ``dms`
    to keep the non-numerical values in the data. 
    
    """
    def __init__(
        self, 
        area:str=None,
        holeid:str=None,
        lat:str=None, 
        lon:str=None, 
        projection:str ='ll', 
        utm_zone:str=None, 
        datum:str='WGS84', 
        epsg:int=None, 
        encoding:str='utf-8', 
        interp_coords:bool=False, 
        reference_ellipsoide:int=23, 
        verbose:bool=False 
        ): 
        
        self.area =area 
        self.holeid=holeid  
        self.projection= projection 
        self.utm_zone=utm_zone 
        self.reference_ellipsoide= reference_ellipsoide 
        self.datum=datum 
        self.encoding= encoding 
        self.epsg =epsg 
        self.interp_coords=interp_coords
        self.lon=lon 
        self.lat=lat 
        self.verbose= verbose 
            
    def fit ( self, data, **fit_params): 
        """ Fit Hole data set and populate attributes. 
        
        Parameters 
        ----------
        data: Path-like Object or DataFrame 
          Hole data. 
          
        fit_params: dict,
          Keyword arguments passed to :func:`watex.to_numeric_dtypes` to 
          sanitize the data. 
          
        Return 
        ------
        self: :class:`DSBoreholes`
          Instanced object for chaining methods. 
          
        """
        columns = fit_params.pop ("columns", None  )
        data = _is_readable(data, as_frame =True, 
                            input_name= 'b', 
                            columns = columns, 
                            encoding =self.encoding 
                            )
        
        data = check_array (
            data, 
            force_all_finite= "allow-nan", 
            dtype =object , 
            input_name="Boreholes data", 
            to_frame=True, 
            )
        self.lon_=None; self.lat_=None 
        
        if ( self.lon is not None 
            and self.lat is not None
            ): 
            p = Profile (utm_zone = self.utm_zone , 
                         coordinate_system= self.projection, 
                         datum= self.datum , 
                         epsg= self.epsg, 
                         reference_ellipsoid=self.reference_ellipsoid 
                         ) 
            p.fit (x = self.lon, y = self.lat, data = data ) 
  
            if self.interp_coords: 
               p.interpolate ()
               
            self.lon_= p.x 
            self.lat_= p.y 
            
        # For consistency, Check the datatype, sanitize columns 
        # and drop all NaN columns and row values
        data, nf, cf = to_numeric_dtypes(
            data , 
            return_feature_types= True, 
            verbose =self.verbose, 
            sanitize_columns= True, 
            fill_pattern='_', 
            **fit_params 
            )

        self.feature_names_in_ = nf + cf 
        
        if len(cf )!=0:
            # sanitize the categorical values 
            for c in cf : 
                data[c] = data[c].str.strip() 
            
        for name in data.columns : 
            setattr (self, name, data[name])
            
        # set depth attributes 
        if 'depth'  in self.feature_names_in_: 
            self.depth_= data['depth']
            
        self.data_ = data.copy() 
        
        use_col =False 
        if self.holeid is not None: 
            use_col = True 
        else: self.holeid ='hole'
            
        self.hole = data2Box ( 
            self.data_ , 
            name =self.holeid, 
            use_colname= use_col
                      )
        
        return self  
    
    def set_coordinates (
        self, 
        reflong, 
        reflat,  
        step ='5m', 
        todms=False, 
        r= 45, 
        **kws
         ): 
        """ Generate longitude and latitude coordinates for boreholes. 
        
        It assumes boreholes are  aligned along the same axis. 
     
        Parameters 
        -----------
        reflong: float or string or list of [start, stop]
            Reference longitude  in degree decimal or in DD:MM:SS for 
            the first site considered as the origin of the landmark.
            
        reflat: float or string or list of [start, stop]
            Reference latitude in degree decimal or in DD:MM:SS for the 
            reference site considered as the landmark origin. If value is 
            given in a list, it can containt the start point and the 
            stop point. 
            
        step: float or str 
            Offset or the distance of seperation between different sites 
            in meters. If the value is given as string type, except 
            the ``km``, it should be considered as a ``m`` value. Only 
            meters and kilometers are accepables.
            
        r: float or int 
            The rotate angle in degrees. Rotate the angle features 
            toward the direction of the projection profile. 
            Default value use the :meth:`~.bearing` value in degrees. 
               
        todms: bool, Default=False
            Reconvert the longitude/latitude degree decimal values into 
            the DD:MM:SS. 
     
        kws: dict, 
           Additional keywords of :func:`~watex.utils.exmath.makeCoords`.   
           
        Returns 
        --------
        self: Instanced object 
        
          Instanced object for method chaining.
        
        """
        self.inspect
        
        nsites = len(self.data_ )
        isutm = False if self.projection =='ll' else True 
        utm_zone =  kws.pop ('utm_zone', None ) or self.utm_zone 
        
        self.lon_, self.lat_= makeCoords(
            reflong, 
            reflat, 
            nsites =nsites, 
            r= r ,  
            step =step , 
            todms=todms, 
            utm_zone= utm_zone, 
            is_utm= isutm, 
            datum=self.datum, 
            espg=self.epsg,
            **kws
            ) 
        
        return self    
        
    def __repr__(self):
        """ Pretty format for programmer guidance following the API... """
        _t = ("name", "dname", "projection", "utm_zone", "encoding", "datum", 
              "epsg", "reference_ellipsoid" ,"interp_coords", "verbose")
        outm = ( '<{!r}:' + ', '.join(
            [f"{k}={ False if getattr(self, k)==... else  getattr(self, k)!r}" 
             for k in _t]) + '>' 
            ) 
        return  outm.format(self.__class__.__name__)
       
    
    def __getattr__(self, name):
       rv = smart_strobj_recognition(name, self.__dict__, deep =True)
       appender  = "" if rv is None else f'. Do you mean {rv!r}'
       
       err_msg =  f'{appender}{"" if rv is None else "?"}' 
       
       raise AttributeError (
           f'{self.__class__.__name__!r} object has no attribute {name!r}'
           f'{err_msg}'
           )

    @property 
    def inspect (self): 
        """ Inspect object whether is fitted or not"""
        msg = ( "{obj.__class__.__name__} instance is not fitted yet."
               " Call 'fit' with appropriate arguments before using"
               " this method"
               )
        
        if not hasattr (self, 'hole'): 
            raise NotFittedError(msg.format(
                obj=self)
            )
        return 1  
    
    
class DSBorehole: 
    """ Class delas with Borehole datasets. 
    
    :class:`watex.geology.drilling.DSBorehole` works with data collected in 
    a single borehole. For instance, it could follow the arrangement of 
    ``h502`` data in :func:`watex.datasets.load_hlogs`
    
    Parameters
    ------------
    name: str
       Name or ID of the borehole. 
      
    dname: str, optional 
       Depth column name. If `depth` is specify an attribute `depth_` should 
       be created. Depth specification is usefull for log plotting of machine
       training.
       
    utm_zone: Optional, string
       zone number and 'S' or 'N' e.g. '55S'. Default to the centre point
       of coordinates points in the survey area. It should be a string (##N or ##S)
       in the form of number and North or South hemisphere, 10S or 03N
       
    projection: str, ['utm'|'dms'|'ll'] 
       The coordinate system in which the data points for the profile is collected. 
       If not given, the auto-detection will be triggered and find the  suitable 
       coordinate system. However, it is recommended to provide it for consistency. 
       Note that if `x` and `y` are composed of value less than 180 degrees 
       for longitude and 90 degrees for latitude, it should be considered as  
       longitude-latitude (``ll``) coordinates system. If `x` and `y` are 
       degree-minutes-second (``dms`` or ``dd:mm:ss``) data, they must be 
       specify as coordinate system in order to accept the non-numerical data 
       before transforming to ``ll``. If ``data`` is passed to the :meth:`.fit`
       method and ``dms`` is not specify, `x` and `y` values should be discarded.
       
    datum: string, default = 'WGS84'
       well known datum ex. WGS84, NAD27, NAD83, etc.

    epsg: Optional, int
       epsg number defining projection (
            see http://spatialreference.org/ref/ for moreinfo)
       Overrides utm_zone if both are provided. 

    reference_ellipsoid: int, default=23 
       reference ellipsoids is derived from Peter H. Dana's website-
       http://www.utexas.edu/depts/grg/gcraft/notes/datum/elist.html
       Department of Geography, University of Texas at Austin
       Internet: pdana@mail.utexas.edu . Default is ``23`` constrained to 
       WGS84. 
        
    encoding: str, default ='utf8'
       Default encoding for parsing data. Can also be ['utf-16-be'] for 
       reading bytes characters. 
       
    lonlat: Tuple, Optional 
       longitude/latitude for borehole coordinates. The location where the 
       borehole is performed. 
      
    verbose: int, default=0 
       Output messages. 
      
    Attributes
    -----------
    depth_: Series 
       Depth array if `dname` is specified. 
    data_: Pandas DataFrame
       Sanitized dataframe. 
    
    Note 
    ------
    Each columns of the dataframe is an attribute. Note that all the non-
    alphabetic letters is removed and replace by '_'. 
    
    """
    def __init__ (
        self,
        name:str=None, 
        dname: str=None,
        projection:str='ll', 
        utm_zone:str=None, 
        datum:str ='WGS84', 
        epsg:int=None, 
        reference_ellipsoid:int=23,
        encoding:str ='utf-8', 
        lonlat:tuple =None, 
        verbose:int= 0, 
        ): 
        
        self.name=name
        self.dname=dname 
        self.projection= projection 
        self.utm_zone=utm_zone 
        self.reference_ellipsoid= reference_ellipsoid 
        self.datum=datum 
        self.encoding= encoding
        self.epsg =epsg 
        self.verbose= verbose 
   
    def fit(self, data,  **fit_params ):
        """ Fit Borehole data and populate attribute data. 
        
        By default if the projection is given as latitude/longitude 
        xlon, ylat are longitude and latitude respectively. 
 
        Parameters
        ------------
        data: pd.DataFrame or Path-like object. 
           Data containing `xlon` and `y` values as series. Then if `xlon` and `y`
           are given as string argument, their names must be included in the 
           data columns. Otherwise an error will raise. 
           
        Return 
        ---------
        self : Instanced object 
            Instanced object for chaining method. 
            
        """
        columns = fit_params.pop ("columns", None  )
        data = _is_readable(data, as_frame =True, input_name= 'b', 
                columns = columns, encoding =self.encoding )
        
        data = check_array (
            data, 
            force_all_finite= "allow-nan", 
            dtype =object , 
            input_name="Borehe data", 
            to_frame=True, 
            )
        
        data, nf, cf = to_numeric_dtypes(
            data , 
            return_feature_types= True, 
            verbose =self.verbose, 
            sanitize_columns= True, 
            fill_pattern='_', 
            **fit_params 
            )

        self.feature_names_in_ = nf + cf 
        
        if len(cf )!=0:
            # sanitize the categorical values 
            for c in cf : 
                data[c] = data[c].str.strip() 
            
        
        for name in data.columns : 
            setattr (self, name, data[name])
            
        # set depth attributes 
        self.depth_= None 
        
        if self.dname is not None: 
            if self.dname not in self.feature_names_in_: 
                self.dname ='depth' 
        
        if self.dname  in self.feature_names_in_: 
            self.depth_= data[self.dname]
            
        self.data_ = data.copy() 
        
        return self 
    
    
    def set_depth ( 
        self ,z0=0.,  max_depth =None, 
        ): 
        """ Set the a random depth if depth is not given.
        
        To fetch the depth, use attribute `depth_`. Note that if the depth 
        exist, calling `set_depth` will arase the former depth value. Use 
        in cautioness. 
        
        Parameters 
        -----------
        z0: float, default=0.
         The surface reference. Preferably, it is set to null. 
         
        max_depth: float, default=700. 
          The maximum depth. Depth size must fit the length of the data in 
          meters. Default depth is fixed to 700 meters. 
          
        Return
        -------
        self: Instanced object 
            Instanced object for chaining method. 
        
        """
        self.inspect 
        z0 = convert_value_in (z0 )
        
        max_depth = 700. if not max_depth else max_depth 

        max_depth = float( _assert_all_types ( max_depth, int, float, 
                                              objname = 'Maximum-depth')) 
 
        self.depth_ = pd.Series ( np.linspace ( z0, max_depth, len(self.data_) 
                                               ), name ='depth')
        # append depth data 
        # self.data_.insert (0 , 'depth', self.depth_, allow_duplicates =True)
        self.data_ = pd.concat ([ self.depth_, self.data_], axis = 1, 
                                ignore_index =True )

        return self 
    
    def set_thickness(self, h0= 1 , **kws ): 
        """ Set a random layer thickness from borehole refering to the depth.
        
        To fetch the thickness, use attribute `layer_thickness_`. 
        
        Parameters 
        -----------
        h0: int, default='1m' 
          Thickness of the first layer. 
          
        shuffle: bool, default=True 
          Shuffle the random generated thicknesses. 

        dirichlet_dis: bool, default=False 
          Draw samples from the Dirichlet distribution. A Dirichlet-distributed 
          random variable can be seen as a multivariate generalization of a 
          Beta distribution. The Dirichlet distribution is a conjugate prior 
          of a multinomial distribution in Bayesian inference.
          
        random_state: int, array-like, BitGenerator, np.random.RandomState, \
             np.random.Generator, optional
          If int, array-like, or BitGenerator, seed for random number generator. 
          If np.random.RandomState or np.random.Generator, use as given.
          
        unit: str, default='m' 
          The reference unit for generated layer thicknesses. Default is 
          ``meters``
        
        Return
        -------
        self: Instanced object 
            Instanced object for chaining method. 
        
        """
        self.inspect 
        
        if self.depth_ is None:
            self.set_depth () 
            
        thickness = get_random_thickness  ( self.depth_, **kws)
        
        self.layer_thickness_= pd.Series (thickness, name='layer_thickness' )
        self.data_ = pd.concat ([  self.data_,  self.layer_thickness_], 
                                axis = 1, ignore_index =True )
        
        return self 
    

    def __repr__(self):
        """ Pretty format for programmer guidance following the API... """
        _t = ("name", "dname", "projection", "utm_zone", "encoding", "datum", 
              "epsg", "reference_ellipsoid" ,"interp_coords", "verbose")
        outm = ( '<{!r}:' + ', '.join(
            [f"{k}={ False if getattr(self, k)==... else  getattr(self, k)!r}" 
             for k in _t]) + '>' 
            ) 
        return  outm.format(self.__class__.__name__)
       
    
    def __getattr__(self, name):
       rv = smart_strobj_recognition(name, self.__dict__, deep =True)
       appender  = "" if rv is None else f'. Do you mean {rv!r}'
       
       err_msg =  f'{appender}{"" if rv is None else "?"}' 
       
       raise AttributeError (
           f'{self.__class__.__name__!r} object has no attribute {name!r}'
           f'{err_msg}'
           )

    @property 
    def inspect (self): 
        """ Inspect object whether is fitted or not"""
        msg = ( "{obj.__class__.__name__} instance is not fitted yet."
               " Call 'fit' with appropriate arguments before using"
               " this method"
               )
        
        if not hasattr (self, 'data_'): 
            raise NotFittedError(msg.format(
                obj=self)
            )
        return 1
    
     
class Borehole(Geology): 
    """
    Focused on Wells and `Borehole` offered to the population. To use the data
    for prediction purpose, each `Borehole` provided must be referenced on 
    coordinates values or provided the same as the one used on `ves` or `erp` 
    file. 
    
    """
    def __init__(
        self,
        lat:float = None, 
        lon:float = None, 
        area:str = None, 
        status:str =None, 
        depth:float = None, 
        base_depth:float =None, 
        geol:str=None, 
        staticlevel:float =None, 
        airlift:float =None, 
        id=None, 
        qmax =None, 
        **kwds
        ): 
       super().__init__(**kwds)
        
       self.lat=lat 
       self.lon=lon 
       self.area=area 
       self.status=status 
       self.depth=depth 
       self.base_depth=base_depth 
       self.geol=geol 
       self.staticlevel=staticlevel 
       self.airlift =airlift 
       self.id=id 
       self.qmax=qmax 
       
       for key in list(kwds.keys()): 
           setattr (self, key, kwds[key])

    
    def fit(self,
            data: str |DataFrame | NDArray 
        )-> object: 
        """ Fit Borehole data and populate the corrsponding attributes"""
        
        self._logging.info ("fit {self.__class__.__name__!r} for corresponding"
                            "attributes. ")
    
        return self
    
class Drill(Geology):
    """
    This class is focus on well logs . How to generate well Log for Oasis:
        
    Arguments
    -----------
    **well_filename** : string ,
        The  well filename. 02 options is set : 
        1rst option is to build well data manually and the program will  
        generate a report.  2nd option is to send to
        the program a typical file type to be parsed . the programm parses
        only the typical well datafile. If None ,  the program will 
        redirect to build mannually option . 
                
    **auto** : bool  
        option to automatically well data . set to True 
         if you want to build manually a well data .
        *default* is False

    ====================  ==========  =========================================    
    Key Words/Attributes  Type          Description    
    ====================  ==========  =========================================   
    utm_zone                str         utm WGS84 zone. should be N or S.   
                                        *default* is 49N .
    compute_azimuth         bool        if no azimuth is provided. 
                                        set to True to letprogram to compute
                                        azimuth .*Default* is False.
    Drill_dip               float       The dip of drill hole.*default* is 90
    Drill_buttom            float       The average bottom of drill , 
                                        can be filled during the well
                                        buiding . *default* is  None
    mask                    int         the mask of DrillHole(DH) data. 
                                        *Default * is 1.
    ====================  ==========  =========================================
    
    ==================  =======================================================
    Methods                   Description
    ==================  =======================================================
    _collar             build _collar data *return*  collar log dataframe 
                        format
     dhGeology          build DH log geology *return* geology log dataframe.        
    dhSample            build DH Geochemistry-Strutural sample, *return* Sample
                        log dataframe    
    dhSurveyElevAz      build DH Elevation & Azimuth logs.*return * Elevation
                        & Azimuth dataframes
    writeDHDATA          output log :* return *  the right log to output for
                        Oasis Montaj 
    ==================  =======================================================
        
    :Example: 
        
    >>> from watex.geoloy.drilling import Drill 
    >>> parser_file ='nbleDH.csv'
    >>> drill_obj=Drill(well_filename='data/drill/drill_example_files')
    >>>  scollar=drill._collar(DH_Top=None)
    >>> sgeo=drill.dhGeology()
    >>> ssam=drill.dhSample()
    >>> selevaz=drill.dhSurveyElevAz( add_elevation=None, 
    ...                             add_azimuth=None)
    >>> swrite=drill.writeDHData(data2write ="*", savepath =None)
    """

    import_optional_dependency ("openpyxl")   
    def __init__(self, well_filename=None , auto=True, **kwargs):
        
        self.wfilename=well_filename
        self.auto=auto
        
        self.mask=kwargs.pop("mask",1)
        self.utm_zone=kwargs.pop("utm_zone","49N")
        self.compute_azimuth=kwargs.pop("compute_azimuth",False)
        self.dip =kwargs.pop("Drill_dip",90)
        self.buttom=kwargs.pop("Drill_buttom", None)
        self.savepath =kwargs.pop('savepath', None )

        
        self.easts=None
        self.norths= None
        self.wellnames= None
        self._f=None 
        
        #populate attribute later 
        self.wdico={"DH_Hole" :None, 
                    "DH_East":None, 
                    "DH_North":None, 
                    "Mask": None,
                    "DH_RH":None, 
                    'DH_From':None , 
                    "DH_To": None , 
                    "Rock": None , 
                    "DH_Azimuth":None , 
                    'DH_Top':None, 
                    'DH_Bottom':None,
                    'DH_PlanDepth':None, 
                    'DH_Decr':None, 
                    'Sample':None,
                    'DH_Dip': None, 
                    'Elevation':None,
                    'DH_RL':None,
                    }        
        
        # if self.auto is False and self.wfilename is None :
            
        #     self.daTA=func.build_wellData (add_azimuth=self.compute_azimuth, 
        #                                     utm_zone=self.utm_zone,
        #                                     report_path = self.savepath, 
        #                                     )
        #     self.wdata=self.daTA[1]
            
        #     self.wdico["DH_East"]   =   self.wdata[:,1]
        #     self.wdico["DH_North"]  =   self.wdata[:,2]
        #     self.wdico["DH_Hole"]   =   self.wdata[:,0]
        #     self.wdico['DH_Dip']    =   self.wdata[:,4]
        #     self.wdico['DH_Bottom'] =   self.wdata[:,3]
        #     self.wdico['DH_Decr'] =   self.wdata[:,7]
        #     self.wdico['DH_PlanDepth'] =   self.wdata[:,6]
        #     self.wdico["DH_Azimuth"] =   self.wdata[:,5]
            
        #     self._f=0


        # elif  self.wfilename is not None :
            
        #     self.daTA=func.parse_wellData(filename=self.wfilename,
        #                                   include_azimuth=False,
        #                                   utm_zone=self.utm_zone)
        #     self.wdata=self.daTA[1]
        #     self.wdico.__setitem__("DH_East", self.wdata[:,1])
        #     self.wdico.__setitem__("DH_North", self.wdata[:,2])
        #     self.wdico.__setitem__("DH_Hole", self.wdata[:,0])
        #     self.wdico.__setitem__('DH_Dip', self.wdata[:,3])
        #     self.wdico.__setitem__('DH_PlanDepth', self.wdata[:,8])
        #     self.wdico.__setitem__("DH_Azimuth", self.wdata[:,5])
        #     self.wdico.__setitem__('DH_Decr', self.wdata[:,9])
        #     self.wdico.__setitem__('DH_Bottom', self.wdata[:,7])
            
        #     self._f=1
            

        #set Mask and set dr_rh
        self.mask=np.full((self.wdata.shape[0]),self.mask,dtype='<U12')
        # print(self.mask.shape)
        self.wdico.__setitem__("Mask", self.mask)
        self.dh_rh=np.zeros((self.wdata.shape[0]))
        self.wdico.__setitem__("DH_RH", self.dh_rh)  

        for keys in kwargs.keys():
            self.__setattr__(keys, kwargs[keys])
            
            
    def _collar(self, DH_Top=None,add_elevation =None ):
        """
        Method to build Collar Data 
        
        Parameters 
        ----------
        * DH_Top  : np.ndarray ,
                it's the Top of data for each Hole Name. 
                ndaray (number of DH , 1) 
                *Default* is None.
        Returns
        -------
        pd.DataFrme 
            collar Drillhole log
        """

        if DH_Top is None :
            DH_Top=np.zeros((self.wdata.shape[0]))
        elif type(DH_Top) is float or type(DH_Top) is int :
            DH_Top=np.full((self.wdata.shape[0]),DH_Top,dtype='<U12')
            
        elif DH_Top is not None :
            if type(DH_Top)==list:
                DH_Top=np.array(DH_Top)
                
            assert DH_Top.shape[0]==self.wdata.shape[0],'the input DH_Top '\
                'shape doesnt match. The convenience '\
                    ' shape is %d.'%self.wdata.shape[0]
        
        # print(DH_Top)
        self.wdico.__setitem__('DH_Top',DH_Top)
        
        if self._f == 0 :
            if add_elevation is None :
                #No topography is added , set to 0 
                add_elevation=np.full((len(self.wdico['DH_East']),1),0,
                                      dtype='<U12')
            elif add_elevation is not None :
                if type(add_elevation ) is list :
                    add_elevation =np.array(add_elevation)
                assert add_elevation.shape[0]==\
                    self.wdico['DH_East'].shape[0],"INDEXERROR:"\
                    " The the current dimention of Elevation data is {0}.It's must be"\
                        " the size {1}.".format(
                            add_elevation.shape[0],self.wdico['DH_East'].shape[0])
            
            self.wdico.__setitem__("Elevation", add_elevation)
                    
        elif self._f == 1 :
            
            if add_elevation is not None:
                
                if type(add_elevation ) is list :
                    add_elevation =np.array(add_elevation)
                try :
                    np.concat((add_elevation,self.wdico['DH_East']))
                except Exception : 
                    mess =''.join([
                        'SIZEERROR! Try to set the elevation dimentional as ', 
                            'same size like the collar data'])
                    self._logging.error(mess)
                    warn(mess)
                    
            elif add_elevation is None :
                add_elevation=self.daTA [1][:,4]
        
            self.wdico.__setitem__("Elevation", add_elevation)
        
        collarKeys=["DH_Hole",	"DH_East",	"DH_North",	"DH_RH",
                    "DH_Dip", "Elevation", "DH_Azimuth","DH_Top", "DH_Bottom",
                    "DH_PlanDepth",	"DH_Decr",	"Mask"] 
        
        # print(self.wdico)
        collar=self.wdico[collarKeys[0]]
        collar=collar.reshape((collar.shape[0],1))
        for ss, collk in enumerate(collarKeys[1:]):  
            # print(collk)
            for key , value in self.wdico.items():
                if key == collk :
                    value=value.reshape((value.shape[0],1))
                    collar=np.concatenate((collar,value), axis=1)
        
        
        self.coLLAR=pd.DataFrame(data=collar, columns=collarKeys)

        return self.coLLAR
    
    
    def dhGeology (self, dh_geomask=None):
        """
        Method to build geology drillhole log. The name of input rock must
        feell exaction accordinag to a convention AGSO file . If not sure
        for the name of rock and Description and label. You may consult
        the geocode folder before building the well_filename. If the entirely
        rock name is given , program will search on the AGSO file the 
        corresponding Label and code . If the rock name is  founc then 
        it will take its CODE else it will generate exception. 
 
        Parameters
        ----------
        * dh_geomask : np.ndarray, optional
                    geology mask. send mask value can take exactly
                    the np.ndarray(num_of_geology set ,). The better way 
                    to set geology maskis to fill on the wellfilename.
                    if not , programm will take the general mask value. 
                    The *default* is None.

        Returns
        -------
        pd.DataFrame 
            geology drillhole log.
        """
        
        
        geolKeys=["DH_Hole","DH_From",	"DH_To","Rock",	"Sample",
                  "East",	"DH_North",	"DH_RH",	"Mask"]
        
        wgeo=self.daTA[2]
        # print(wgeo)
        
        self.wdico.__setitem__('DH_From', wgeo[:,1])
        self.wdico.__setitem__('DH_To', wgeo[:,2])
        self.wdico.__setitem__("Rock",wgeo[:,3])
        dhgeopseudosamp=np.zeros((wgeo.shape[0]))
        
        ###### FIND AGSO MODULE #######
        #Try to check the name of rocks and their acronym
        geoelm= get_agso_properties()
            # #extract elem with their acronym 
        geolemDico_AGSO={key:value for key , value in \
                         zip (geoelm["CODE"],geoelm['__DESCRIPTION'])}
        # elemgeo_AGSO=sorted(geolemDico.items())
        for ii, elm in enumerate (self.wdico['Rock']):
            if elm.upper() in geolemDico_AGSO.keys():
                pass 
            elif elm.upper() not in geolemDico_AGSO.keys():
                if elm.lower() in geolemDico_AGSO.values():
                    for key, values in geolemDico_AGSO.items():
                        if elm.lower() == values :
                            self.wdico['Rock'][ii]=key
                else  :
                    mess=''.join(['The Geological Name ({0})'
                                  ' given in is wrong'.format(elm),
                                'Please provide a right name the right Name.', 
                                'Please consult the AGSO file in _geocodes folder', 
                                'without changing anything.'])
                    self._logging.warn(mess)
                    warn(mess)

        ######END AGS0 ########
        
        self.dh_geoleast=np.zeros((wgeo.shape[0]))
        self.dh_geol_norths=np.zeros((wgeo.shape[0]))
        
        for ss , value in enumerate(self.dh_geoleast):
            for indix, val in enumerate(self.wdico["DH_East"]):
                if wgeo[:,0][ss] in self.wdico["DH_Hole"]:
                    value=val
                    self.dh_geoleast[ss] =value
                    self.dh_geol_norths[ss]=self.wdico["DH_North"][indix]
                    
        dhgeopseudosamp=np.zeros((wgeo.shape[0]))

        if dh_geomask == None :
            dh_geomask =self.mask[0]
        maskgeo= np.full((wgeo.shape[0]),dh_geomask,dtype='<U12')
        dhrhgeo=np.array([ -1* np.float(ii) for ii in self.wdico['DH_From']])
        dhGeol=np.concatenate((wgeo[:,0].reshape(wgeo[:,0].shape[0],1),
                              self.wdico['DH_From'].reshape((
                                  self.wdico['DH_From'].shape[0],1)),
                              self.wdico['DH_To'].reshape((
                                  self.wdico['DH_To'].shape[0],1)),
                              self.wdico['Rock'].reshape((
                                  self.wdico['Rock'].shape[0],1)),
                              dhgeopseudosamp.reshape((
                                  dhgeopseudosamp.shape[0],1)),
                              self.dh_geoleast.reshape((
                                  self.dh_geoleast.shape[0],1)),
                              self.dh_geol_norths.reshape((
                                  self.dh_geol_norths.shape[0],1)),
                              dhrhgeo.reshape((dhrhgeo.shape[0],1)),
                              maskgeo.reshape((maskgeo.shape[0],1))),axis=1)
        self.geoDHDATA=pd.DataFrame(data=dhGeol, columns=geolKeys)
        
        return self.geoDHDATA
    
           
    def dhSample (self,path_to_agso_codefile=None, dh_sampmask=None):
        """
        Method to build Sample log. This method focuses on the sample obtained 
        during the DH trip.it may georeferenced as the well_filename needed. 
        A main thing is to set the AGSO_STCODES file. AGSO_STCODES is the 
        conventional code of structurals sample. If you have an own AGSO_STCODES ,
        you may provide the path * kwargs=path_to_ags_codefile * . 
        the program will read and generate logs according to the  DESCRIPTION 
        and STCODES figured. if None, the program will take it STCODES  and set
        the samplelogs. When you set the Sample code aor sample name , 
        make sur that the name match the same name on STCODES. If not ,
        program will raises an error. 

        Parameters
        ----------
        * path_to_agso_codefile : str, optional
                            path to conventional
                            AGSO_STRUCTURAL CODES.
                            The *default* is None.
                            
        * dh_sampmask : np.ndarray, optional
                        Structural mask. The default is None.

        Returns
        -------
        pd.DataFrame 
            Sample DH log.
        """
        
        sampKeys=["DH_Hole","DH_From",	"DH_To","Rock",	"Sample",
                  "East",	"DH_North",	"DH_RH",	"Mask"]
        
        wsamp=self.daTA[3]
        # print(wgeo)
        if wsamp is None :
            self.sampleDHDATA = None 
            return  # mean no geochemistry sample is provided 
        
        self.wdico.__setitem__('DH_From', wsamp[:,1])
        self.wdico.__setitem__('DH_To', wsamp[:,2])
        self.wdico.__setitem__("Sample",wsamp[:,3])
        dhsampseudorock=np.zeros((wsamp.shape[0]))
        
        ###### FIND AGSO MODULE (AGSO_STCODES) #######
        #Try to check the name of sample and their acronym
        
        if path_to_agso_codefile is None:
            path_to_agso_codefile=os.path.join(os.path.abspath('.'),
                                             'watex/etc/_geocodes' )
            sampelm= get_agso_properties(
                config_file = os.path.join(path_to_agso_codefile,
                                           'AGSO_STCODES.csv') )
            # #extrcat elem with their acronym 
        sampelmDico_AGSO={key:value for key , value in \
                         zip (sampelm["CODE"],sampelm['__DESCRIPTION'])}
        # elemgeo_AGSO=sorted(geolemDico.items())

        for ii, elm in enumerate (self.wdico['Sample']):
            if elm.lower() in sampelmDico_AGSO.keys():
                pass 
            elif elm.lower() not in sampelmDico_AGSO.keys():
                if elm in sampelmDico_AGSO.values():
                    for key, values in sampelmDico_AGSO.items():
                        if elm  == values :
                            self.wdico['Sample'][ii]=key
                else  :
                    mess=''.join([
                        'The Sample Name({0}) given in is wrong'.format(elm),
                        'Please provide a right name the right Name.', 
                        'Please consult the AGSO_STCODES.csv file located in ', 
                        '<watex/etc/_geocodes> dir. Please keep the'
                        '  header safe and untouchable.'])
                    self._logging.warn(mess)
                    warn(mess)

        ######END AGS0_STCODES ########
        
        dh_sampeast=np.zeros((wsamp.shape[0]))
        dh_sampnorths=np.zeros((wsamp.shape[0]))
        
        for ss , value in enumerate(dh_sampeast):
            for indix, val in enumerate(self.wdico["DH_East"]):
                if wsamp[:,0][ss] in self.wdico["DH_Hole"]:
                    value=val
                    dh_sampeast[ss] =value
                    dh_sampnorths[ss]=self.wdico["DH_North"][indix]
                    
        dhsampseudorock=np.zeros((wsamp.shape[0]))

        if dh_sampmask == None :
            dh_sampmask =self.mask[0]
        masksamp= np.full((wsamp.shape[0]),dh_sampmask,dtype='<U12')
        dhrhsamp=np.array([ -1* np.float(ii) for ii in self.wdico['DH_From']])
        dhSample=np.concatenate((wsamp[:,0].reshape(wsamp[:,0].shape[0],1),
                              self.wdico['DH_From'].reshape(
                                  (self.wdico['DH_From'].shape[0],1)),
                              self.wdico['DH_To'].reshape(
                                  (self.wdico['DH_To'].shape[0],1)),
                              dhsampseudorock.reshape(
                                  (dhsampseudorock.shape[0],1)),
                              self.wdico['Sample'].reshape(
                                  (self.wdico['Sample'].shape[0],1)),
                              dh_sampeast.reshape(
                                  (dh_sampeast.shape[0],1)),
                              dh_sampnorths.reshape(
                                  (dh_sampnorths.shape[0],1)),
                              dhrhsamp.reshape((dhrhsamp.shape[0],1)),
                              masksamp.reshape((masksamp.shape[0],1))),axis=1)
        self.sampleDHDATA=pd.DataFrame(data=dhSample, columns=sampKeys)
        
        return self.sampleDHDATA
    
    def dhSurveyElevAz(self, add_elevation=None, add_azimuth=None, **kwargs):
        """
        Method to build Elevation & Azimuth DH logs. if add_elevation and . 
        add_azimuth are set . The programm will ignore the computated azimuth,
        and it will replace to the new azimuth   provided . all elevation will 
        be ignore and set by the new elevation . *kwargs arguments 
        {add_elevation , add-azimuth }  must match the same size like the 
        number of Drillholes . Each one must be on ndarray(num_of_holes, 1). 
        
        Parameters
        ----------
            * add_elevation : np.nadarray , optional
                    elevation data (num_of_holes, 1) 
                    The *default* is None.
                    
            * add_azimuth : np.ndarray , optional
                    azimuth data (num_of_holes,1). 
                    The *default* is None.
                    
            * DH_RL :np.float or np.ndarray(num_of_hole,1),
                    if not provided , it's set to 0. means No topography is added'.
                
        Returns
        -------
            pd.Dataframe 
                Elevation DH log .
            pd.DataFrame 
                Azimuth DH log.
        """
        dh_rl=kwargs.pop("DH_RL",None)
        
        # sizep=self.wdico['DH_East'].shape[0]
        if self._f == 0 :
            if add_elevation is None :
                #No topography is added , set to 0 
                add_elevation=np.full((len(self.wdico['DH_East']),1),0,
                                      dtype='<U12')
            elif add_elevation is not None :
                if type(add_elevation ) is list :
                    add_elevation =np.array(add_elevation)
                assert add_elevation.shape[0]==self.wdico[
                    'DH_East'].shape[0],"INDEXERROR:"\
                    " The the current dimention of Elevation data is {0}.It's must be"\
                        " the size {1}.".format(
                            add_elevation.shape[0],self.wdico['DH_East'].shape[0])
            
            self.wdico.__setitem__("Elevation", add_elevation)
                    
        elif self._f == 1 :
            
            if add_elevation is not None:
                
                if type(add_elevation ) is list :
                    add_elevation =np.array(add_elevation)
                try :
                    np.concat((add_elevation,self.wdico['DH_East']))
                except :
                    mess= ''.join([
                        'SIZEERROR! Try to set the elevation dimentional. ', 
                        'same like the collar data '])
                    self._logging.error(mess)
                    warn(mess)
            elif add_elevation is None :
                add_elevation=self.daTA [1][:,4]
        
            self.wdico.__setitem__("Elevation", add_elevation)
            
        #set DH_RL
        if dh_rl is not None : 
            if type (dh_rl) is list : 
                dh_rl=np.array (dh_rl)
            assert dh_rl.shape[0]==self.data.shape[0]," DH_RL data size is out"\
                " of the range.Must be {0}".format(self.data.shape[0])
                
            self.wdico.__setitem__("DH_RL",dh_rl)
            
        elif dh_rl is None :
            #if None set DH_RL to None :
            self.wdico.__setitem__("DH_RL",np.full(
                (self.daTA[1].shape[0]),0,dtype='<U12'))
        
        #set azimuth 
        if add_azimuth  is not None : 
            if type(add_azimuth) ==list : 
                add_azimuth=np.array(add_azimuth)
            assert add_azimuth.shape[0]==self.data.shape[0]," Azimuth data size is out"\
                " of the range.Must be {0}".format(self.data.shape[0])
                
            self.wdico.__setitem__("DH_Azimuth",add_azimuth) 
            
        elif add_azimuth is None : 
            pass 
                
        elevazKeys=['DH_Hole', 'Depth','DH_East',
                    'DH_North','Elevation','DH_RL','DH_Dip']
        
        self.wdico.__setitem__("DH_RL",np.full(
            (self.daTA[1].shape[0]),0,dtype='<U12'))
        # add Hole and Depth 
        
        surveyELEV =np.concatenate((self.wdico['DH_Hole'].reshape(
            (self.wdico['DH_Hole'].shape[0],1)),
                                    self.wdico["DH_Bottom"].reshape(
             (self.wdico["DH_Bottom"].shape[0],1))),
                                       axis=1)
        surveyAZIM=np.concatenate((self.wdico['DH_Hole'].reshape(
            (self.wdico['DH_Hole'].shape[0],1)),
                                    self.wdico["DH_Bottom"].reshape(
             (self.wdico["DH_Bottom"].shape[0],1))),
                                      axis=1)
        
        for ss , elm in enumerate (elevazKeys[2:]):
            for key, values in self.wdico.items():
                if elm==key :
                    values=values.reshape((values.shape[0],1))
                    if elm =='DH_RL'or elm=='DH_Dip':
                        # print(values)
                        surveyAZIM=np.concatenate((surveyAZIM,values),axis=1)
                    elif  elm=='Elevation':
                        surveyELEV =np.concatenate((surveyELEV,values),axis=1)
                    else:
                        surveyAZIM=np.concatenate((surveyAZIM,values),axis=1)
                        if ss < elevazKeys.index('Elevation')-1: 
                            surveyELEV =np.concatenate((surveyELEV,values),axis=1)
                            
        
        self.surveyDHELEV=pd.DataFrame(
            data=surveyELEV, columns=elevazKeys[:5])
        # pop the elevation elm on the list 
        [elevazKeys.pop(ii) for ii, elm in 
         enumerate(elevazKeys) if elm=='Elevation']
        
        self.surveyDHAZIM=pd.DataFrame(data=surveyAZIM, 
                                       columns=elevazKeys)
        
        return (self.surveyDHELEV, self.surveyDHAZIM)
        
                    
    def writeDHData (self, data2write =None ,**kwargs):
        """ 
        Method to write allDH logs. It depends to the users to sort which data 
        want to export and which format. the program support only two format 
        (.xlsx and .csv) if one is set , it will ouptput the convenience format.
        Users can give a list of  the name of log he want to export.
        Program is dynamic and flexible. It tolerates quite symbols number to
         extract data logs. 
        
        Parameters
        ----------
        * data2write : str or list , optional
                    the search key. The default is None.
        
        * datafn :str
                savepath to exported file 
                *Default* is current work directory.
                
        * write_index_on_sheet : bool, 
                choice to write the sheet with pandas.Dataframe index. 
                
        * writeType : str , 
                file type . its may *.csv or *.xlsx .
                *Default* is *.xlsx
                
        * add_header : bool, 
                add head on exported sheet. set False to mask heads. 
                *Default* is True. 
                
        * csv_separateType : str , 
                Indicated for csv exported files , 
                the type of comma delimited . defaut is ','.
        """
    
        savepath =kwargs.pop("savepath",None )
        writeIndex=kwargs.pop('write_index_on_sheet',False)
        writeType =kwargs.pop('writeType', 'xlsx')
        # csvencoding =kwargs.pop('encoding','utf-8')
        csvsetHeader =kwargs.pop('add_header',True)
        csvsep =kwargs.pop('csv_separateType',',')
        
        
        wDATA ={"collar": self._collar,
                 "geology": self.dhGeology,
                 'sample':self.dhSample,
                 'elevazim':self.dhSurveyElevAz}
        
        _all=['5',"all","__all__",'CollGeoSampElevAz','CGSAZ','cgsaz',
              ['Collar','Geology','Sample','Elevation','Azimuth'],
              'colgeosamelevaz','alldata','*']
        
        df_collar=wDATA['collar']()
        df_geology=wDATA['geology']()
        df_sample=wDATA['sample']()
        df_elevation,df_azimuth=wDATA['elevazim']()
        
        # for df_ in  [df_collar, df_geology, df_sample,
        # df_elevation,df_azimuth]: 
        # df_.set_index(setIndex) # this is unnecessary 
        _dHDico ={'collar': [['1','c'], df_collar],
                 'geology':[['2','g'],df_geology],
                 'sample': [['3','s'],df_sample],
                 'survey_elevation':[['4','elev', 'topo','topography','e'],
                                     df_elevation],
                 'survey_azimuth': [['5','-1','azim','a'],df_azimuth]}
        # skip the sample building  geochemistry doesnt exists
        if self.sampleDHDATA is None :   
            data2write =['1','2','4','5']
          
        if data2write is None or data2write in _all :  # write all 
            with pd.ExcelWriter(''.join([self.daTA[0][:-1],'.xlsx'])) as writer :
                for keys, df_ in _dHDico.items():
                    df_[1].to_excel(writer,sheet_name=keys, index =writeIndex)

                                
        elif data2write is not None :
            
            if type(data2write) is not list:
                data2write=str(data2write)

                try :
                    if writeType in ['xlsx','.xlsx', 'excell',
                                     'Excell','excel','Excel','*.xlsx']:
                        for keys, df in _dHDico.items():
                            if data2write ==keys or data2write.lower(
                                    ) in keys or  data2write in df[0]:
                              df[1].to_excel('.'.join(
                                  [self.daTA[0][:-1],'xlsx']),
                                  sheet_name=keys,index =writeIndex)  

                        
                    elif writeType in ['csv','.csv', 'comma delimited','*.csv',
                                       'comma-separated-value',
                                       'comma seperated value',
                                       'comsepval']:
                        # print('passed')
                        for keys, df_ in _dHDico.items():
                            if data2write == keys or data2write.lower(
                                    ) in keys or data2write in df_[0]:
                              df_[1].to_csv(''.join(
                                  [self.daTA[0][:-1],'.csv']),
                                  header=csvsetHeader,
                                    index =writeIndex,sep=csvsep)  

                except Exception as error :
                    self._logging.error (
                        'The type you provide as WriteType argument is wrong.'
                                ' Support only *.xlsx and *.csv format',error)
                    warn (
                        'Argument writeType support only [xlsx or csv] format.'
                        ' Must change your *.{0} format'.format(writeType))

                
            elif type(data2write) is list :
                data2write=[str(elm) for elm in data2write] # check the string format
                with pd.ExcelWriter(''.join(
                        [self.daTA[0][:-1],'xlsx'])) as writer :
                    for ii, df in enumerate (data2write):
                        for keys, df__ in _dHDico.items():
                            if df.lower() in keys or df in df__[0] : 
                                df__[1].to_excel(
                                    writer,sheet_name=keys, index =writeIndex)
            else :
                self._logging.error (
                    'The key you provide  as agrument of data2write is wrong. '
                    'the data2write argument should be either [collar, geology,'
                        ' sample, elevation, azimuth] or all (*). ')
                warn (
                    'Wrong format of input data2write ! Argument dataType is str,'
                    ' or list of string element choosen among [collar, geology,'
                        'sample, elevation, azimuth] or all (*),'
                        ' not {0}'.format(data2write))
 
         # export to savepath 
        if savepath is not None : self.savepath = savepath 
        # create a folder in your current work directory
        if self.savepath is None : 
            try :
                self.savepath  = os.path.join(os.getcwd(), '_outputDH_')
                if not os.path.isdir(self.savepath):
                    os.mkdir(self.savepath)#  mode =0o666)
            except : 
                warn("It seems the path already exists !")
        
        
        if self.savepath is not None  :
            import shutil
            
            if writeType in ['csv','.csv', 'comma delimited',
                             'comma-separated-value','comma sperated value',
                                       'comsepval']:
                shutil.move ( os.path.join(os.getcwd(),
                                           ''.join(
                                               [self.daTA[0][:-1],'csv'])),
                             self.savepath)
                print('---> Borehole output <{0}> has been written to {1}.'.\
                      format(os.path.basename(
                    ''.join([self.daTA[0][:-1],'.csv'])), self.savepath))
                
            elif writeType in ['xlsx','.xlsx', 'excell','Excell','excel','Excel']:
                try :
                    shutil.move (os.path.join(os.getcwd(),
                                               '.'.join([self.daTA[0][:-1],'xlsx'])),
                                 self.savepath)
                except: 
                    print("--> It seems the destination path "
                          f"{self.savepath} already exists")
                
                print('---> Borehole output <{0}> has been written to {1}.'.\
                      format(os.path.basename(
                      '.'.join([self.daTA[0][:-1],'xlsx'])), self.savepath))