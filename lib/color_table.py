'''
File: color_table.py
Author: Min Feng
Version: 0.1
Create: 2016-10-21 18:43:37
Description:
'''

import logging

def map_colortable(cs):
    from osgeo import gdal

    _color_tables = gdal.ColorTable()
    for i in range(256):
        if i in cs:
            _color_tables.SetColorEntry(i, tuple(cs[i] if len(cs[i]) >= 4 else (list(cs[i]) + [255])))

    _color_tables.SetColorEntry(255, (0,0,0,0))
    return _color_tables

class color_table:

    def __init__(self, ccs):
        _rs = ccs if isinstance(ccs, dict) else self._load_color_file(ccs)
        
        for _r, _v in _rs.items():
            if len(_v) == 3:
                _rs[_r] = list(_v) + [255]
                
        self._colors = _rs
        
    def _load_qgis_colors(self, ls):
        _ls = ls[2:]
    
        _cs = {}
        _n = 0
    
        for _l in _ls:
            _vv = _l.split(',')
            if len(_vv) != 6:
                continue
    
            _cc = tuple(map(int, _vv[1:5]))
            _cs[int(_vv[0])] = _cc
    
            _n += 1
    
        if _n <= 0:
            raise Exception('no color entries found')
    
        return _cs

    def _load_color_file(self, f):
        import re
        from gio import file_mag

        _colors = {}
        with open(file_mag.get(f).get()) as _fi:
            _ls = _fi.read().strip().splitlines()
            if len(_ls) == 0:
                raise Exception('color table is empty')

            if f.endswith('.csv') or 'QGIS' in _ls[0]:
                return self._load_qgis_colors(_ls)
                
            for _l in _ls:
                _l = _l.strip()
                if not _l:
                    continue

                _vs = re.split('\s+', _l, maxsplit=1)
                if len(_vs) != 2:
                    logging.warning('ignore color entry: %s' % _l)
                    continue

                _cs = tuple([int(_v) for _v in re.split('\W+', _vs[1])])
                if len(_cs) < 3:
                    raise Exception('insufficent color values %s' % len(_cs))
                _colors[float(_vs[0])] = _cs

        return _colors

    def _color(self, c):
        if len(c) < 3:
            raise Exception('insufficant color values %s' % c)

        _c = list(c)
        if len(c) == 3:
            _c.append(255)

        return tuple(_c)

    def write(self, f):
        _ls = []
        
        _cs = self._colors
        for _v in sorted(_cs.keys()):
            _ls.append('%s\t%s' % (_v, ','.join(map(str, _cs[_v]))))
        
        from gio import file_unzip
        with file_unzip.zip() as _zip:
            _zip.save('\n'.join(_ls), f)
            
    def colors(self):
        return self._colors

    def ogr_color_table(self):
        return map_colortable(self._colors)
        
class color_mapping:
    
    def __init__(self, cls, clip=False, color_num=256):
        self._inp_colors = cls
        self._clip = clip
        self._color_num = color_num
        
        self._gen_color_table(self._inp_colors.colors())
    
    def _gen_color_table(self, rs):
        _vs = list(sorted(rs.keys()))
        _cs = [rs[_v] for _v in _vs]
        
        _colors = {}
        _values = {}

        _num = self._color_num
        if len(_vs) == _num:
            for _r in range(_num):
                _values[_r] = _vs[_r]
                _colors[_r] = _cs[_r]
                
        else:
            _div = _num // (len(_vs) - 1)
    
            for i in range(len(_vs) - 1):
                _a = _vs[i]
                _d = (_vs[i+1] - _vs[i]) / float(_div)
    
                for _n in range(_div):
                    _v, _c = self._interpolate(_vs, _cs, _a, _num, _div)
    
                    if _v not in _values:
                        _values[_a] = _v
                        _colors[_v] = _c
    
                    _a += _d
                    
            _v, _c = self._interpolate(_vs, _cs, _vs[-1], _num, _div)
            
            if _v not in _values:
                _values[_a] = _v
                _colors[_v] = _c

        self._values = _values
        self._colors = color_table(_colors)

        self._v_min = min(self._values.keys())
        self._v_max = max(self._values.keys())

        if self._v_min < 0 or self._v_max > 255:
            raise Exception('only accept value range between 0 and 255')
            
    def _to_dist(self, vs):
        _w = float(sum([_v['dist'] for _v in vs]))

        _ps = []
        _cs = []

        for _v in vs:
            _w1 = (1.0 - _v['dist'] / _w)

            _ps.append(_w1 * _v['pos'])
            _cs.append([_w1 * _c for _c in _v['color']])

        _p = int(sum(_ps))
        _c = [int(sum([_c[_i] for _c in _cs])) for _i in range(4)]

        return _p, _c

    def _interpolate(self, vs, cs, v, n, div):
        _vs = vs
        _cs = cs
        
        if v >= _vs[-1]:
            return n-1, _cs[-1]

        _v = max(min(_vs), min(v, max(_vs) - 0.000000000001))
        _dv = div

        _pp = 0.0
        for _i in range(len(_vs) - 1):
            _ds = abs(_v - _vs[_i])
            _ps = int(_pp)
            
            if _ds < 0.00000000001:
                return _ps, _cs[_i]

            if _vs[_i] < _v < _vs[_i+1]:
                _vv = []

                _vv.append({'idx': _i, 'pos': _ps, 'value': _vs[_i], 'color': _cs[_i], 'dist': float(_ds)})

                _ds = abs(_v - _vs[_i + 1])
                _ps = int(_pp + _dv)
                _vv.append({'idx': _i+1, 'pos': _ps, 'value': _vs[_i+1], 'color': _cs[_i+1], 'dist': float(_ds)})

                return self._to_dist(_vv)
            else:
                _pp += _dv

        raise Exception('failed to find value %s' % v)

    def get_code(self, v):
        if v < self._v_min:
            if self._clip:
                return 255
            return self._values[self._v_min]
            
        if v > self._v_max:
            if self._clip:
                return 255
            return self._values[self._v_max]

        _vs = []
        for _v in list(self._values.keys()):
            if _v == v:
                return self._values[_v]

            _vs.append({'d': abs(_v - v), 'c': self._values[_v]})

        _cc = sorted(_vs, key=lambda x: x['d'])[0]['c']
        return _cc

    def get_color(self, v):
        _c = self.get_code(v)

        if _c >= 255 or _c not in self._colors._colors:
            return [0, 0, 0, 0]

        return self._colors._colors[_c]
    
def load(f):
    return color_table(f).ogr_color_table()
    