import {ContinuousScale} from "models/scales/continuous_scale"
import * as p from "core/properties"

export namespace ToggleableScale {
    export type Attrs = p.AttrsOf<Props>
  
    export type Props = ContinuousScale.Props & {
        options: p.Property<ContinuousScale[]>,
        active: p.Property<number>
    }
  }
  
  export interface ToggleableScale extends ToggleableScale.Attrs {}
  
  export class ToggleableScale extends ContinuousScale {
    properties: ToggleableScale.Props
  
    _last_index: number

    constructor(attrs?: Partial<ToggleableScale.Attrs>) {
      super(attrs)
    }
  
    static init_ToggleableScale() {
      this.define<ToggleableScale.Props>(({Int, Array, Ref})=>({
        options:  [Array(Ref(ContinuousScale)), []],
        active: [Int, 0]
      }))
      }

    initialize(): void {
        super.initialize()
        const {options, active, target_range, source_range} = this
        //this._last_index = active
        const current_scale = options[active]
        current_scale.target_range = target_range
        current_scale.source_range = source_range
      }

    connect_signals(): void {
        super.connect_signals()

        this.connect(this.properties.active.change, () => this.on_active_change())
    }

    on_active_change() {
        const {active, options} = this
        const current_scale = options[active]
        current_scale.target_range = this.target_range
        current_scale.source_range = this.source_range
        this.properties.target_range.change.emit()
        //this._last_index = active
    }

    get s_compute(){
        const {active, options, source_range, target_range} = this
        const current_scale = options[active]
        current_scale.target_range = target_range
        current_scale.source_range = source_range
        return current_scale.s_compute
    }

    get s_invert(){
        const {active, options, source_range, target_range} = this
        const current_scale = options[active]
        current_scale.target_range = target_range
        current_scale.source_range = source_range
        return current_scale.s_invert
    }

  }
