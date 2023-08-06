import { Mark } from 'vega';
import { VgEncodeEntry, VgPostEncodingTransform } from '../../vega.schema';
import { UnitModel } from '../unit';
/**
 * Abstract interface for compiling a Vega-Lite primitive mark type.
 */
export interface MarkCompiler {
    /**
     * Underlying Vega Mark type for the Vega-Lite mark.
     */
    vgMark: Mark['type'];
    encodeEntry: (model: UnitModel) => VgEncodeEntry;
    /**
     * Transform on a mark after render, used for layout and projections
     */
    postEncodingTransform?: (model: UnitModel) => VgPostEncodingTransform[];
}
//# sourceMappingURL=base.d.ts.map