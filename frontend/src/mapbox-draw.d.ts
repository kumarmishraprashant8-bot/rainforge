declare module '@mapbox/mapbox-gl-draw' {
    import { IControl } from 'mapbox-gl';

    interface DrawOptions {
        displayControlsDefault?: boolean;
        controls?: {
            polygon?: boolean;
            trash?: boolean;
            point?: boolean;
            line_string?: boolean;
            combine_features?: boolean;
            uncombine_features?: boolean;
        };
        defaultMode?: string;
    }

    class MapboxDraw implements IControl {
        constructor(options?: DrawOptions);
        onAdd(map: mapboxgl.Map): HTMLElement;
        onRemove(map: mapboxgl.Map): void;
        getAll(): GeoJSON.FeatureCollection;
        deleteAll(): void;
        set(featureCollection: GeoJSON.FeatureCollection): void;
    }

    export default MapboxDraw;
}
