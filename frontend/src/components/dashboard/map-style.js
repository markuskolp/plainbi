import {FillLayer} from 'react-map-gl';

// For more information on data-driven styles, see https://www.mapbox.com/help/gl-dds-ref/
export const dataLayer = {
  id: 'data',
  type: 'fill',
  paint: {
    'fill-color': {
      property: 'percentile',
      stops: [
        [0, '#3288bd'],
        [1, '#66c2a5'],
        [2, '#abdda4'],
        [3, '#e6f598'],
        [4, '#ffffbf'],
        [5, '#fee08b'],
        [6, '#fdae61'],
        [7, '#f46d43'],
        [8, '#d53e4f']
      ]
    },
    'fill-opacity': 0.8
  }
};

export const defaultFillLayer = {
    id: 'defaultfill',
    type: 'fill',
    paint: {
      'fill-color': '#3388ff',
      'fill-opacity': 0.2
    }
};

export const defaultLineLayer = {
    id: 'defaultline',
    type: 'line',
    paint: {
      'line-color': '#3388ff',
      'line-width': 2
    }
};