import { parseSelector } from 'vega-event-selector';
import { X, Y } from '../../channel';
import { BRUSH as INTERVAL_BRUSH } from './interval';
import scalesCompiler, { domain } from './scales';
const ANCHOR = '_translate_anchor';
const DELTA = '_translate_delta';
const translate = {
    defined: selCmpt => {
        return selCmpt.type === 'interval' && selCmpt.translate;
    },
    signals: (model, selCmpt, signals) => {
        const name = selCmpt.name;
        const hasScales = scalesCompiler.defined(selCmpt);
        const anchor = name + ANCHOR;
        const { x, y } = selCmpt.project.hasChannel;
        let events = parseSelector(selCmpt.translate, 'scope');
        if (!hasScales) {
            events = events.map(e => ((e.between[0].markname = name + INTERVAL_BRUSH), e));
        }
        signals.push({
            name: anchor,
            value: {},
            on: [
                {
                    events: events.map(e => e.between[0]),
                    update: '{x: x(unit), y: y(unit)' +
                        (x !== undefined ? `, extent_x: ${hasScales ? domain(model, X) : `slice(${x.signals.visual})`}` : '') +
                        (y !== undefined ? `, extent_y: ${hasScales ? domain(model, Y) : `slice(${y.signals.visual})`}` : '') +
                        '}'
                }
            ]
        }, {
            name: name + DELTA,
            value: {},
            on: [
                {
                    events,
                    update: `{x: ${anchor}.x - x(unit), y: ${anchor}.y - y(unit)}`
                }
            ]
        });
        if (x !== undefined) {
            onDelta(model, selCmpt, x, 'width', signals);
        }
        if (y !== undefined) {
            onDelta(model, selCmpt, y, 'height', signals);
        }
        return signals;
    }
};
export default translate;
function onDelta(model, selCmpt, proj, size, signals) {
    var _a, _b;
    const name = selCmpt.name;
    const anchor = name + ANCHOR;
    const delta = name + DELTA;
    const channel = proj.channel;
    const hasScales = scalesCompiler.defined(selCmpt);
    const signal = signals.filter(s => s.name === proj.signals[hasScales ? 'data' : 'visual'])[0];
    const sizeSg = model.getSizeSignalRef(size).signal;
    const scaleCmpt = model.getScaleComponent(channel);
    const scaleType = scaleCmpt.get('type');
    const reversed = scaleCmpt.get('reverse'); // scale parsing sets this flag for fieldDef.sort
    const sign = !hasScales ? '' : channel === X ? (reversed ? '' : '-') : reversed ? '-' : '';
    const extent = `${anchor}.extent_${channel}`;
    const offset = `${sign}${delta}.${channel} / ${hasScales ? `${sizeSg}` : `span(${extent})`}`;
    const panFn = !hasScales
        ? 'panLinear'
        : scaleType === 'log'
            ? 'panLog'
            : scaleType === 'symlog'
                ? 'panSymlog'
                : scaleType === 'pow'
                    ? 'panPow'
                    : 'panLinear';
    const arg = !hasScales
        ? ''
        : scaleType === 'pow'
            ? `, ${(_a = scaleCmpt.get('exponent')) !== null && _a !== void 0 ? _a : 1}`
            : scaleType === 'symlog'
                ? `, ${(_b = scaleCmpt.get('constant')) !== null && _b !== void 0 ? _b : 1}`
                : '';
    const update = `${panFn}(${extent}, ${offset}${arg})`;
    signal.on.push({
        events: { signal: delta },
        update: hasScales ? update : `clampRange(${update}, 0, ${sizeSg})`
    });
}
//# sourceMappingURL=translate.js.map