import {Model} from "model"
import * as p from "core/properties"

// TODO: Create default reducers for moments (count, mean, std), min/max and quantiles

export namespace CustomJSNAryFunction {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Model.Props & {
    parameters: p.Property<Record<string, any>>
    fields: p.Property<Array<string>>
    func: p.Property<string>
    v_func: p.Property<string>
  }
}

export interface CustomJSNAryFunction extends CustomJSNAryFunction.Attrs {}

export class CustomJSNAryFunction extends Model {
  properties: CustomJSNAryFunction.Props

  constructor(attrs?: Partial<CustomJSNAryFunction.Attrs>) {
    super(attrs)
  }

  static __name__ = "CustomJSNAryFunction"

  static init_CustomJSNAryFunction() {
    this.define<CustomJSNAryFunction.Props>(({Array, String})=>({
      parameters:  [p.Instance, {}],
      fields: [Array(String), []],
      func:    [ String ],
      v_func:  [String]
    }))
  }

  initialize(){
    super.initialize()
    this.update_func()
    this.update_vfunc()
  }

  args_keys: Array<string>
  args_values: Array<any>

  scalar_func: Function
  vector_func: Function

  connect_signals(): void {
    super.connect_signals()
  }

  update_func(){
    this.args_keys = Object.keys(this.parameters)
    this.args_values = Object.values(this.parameters)
    this.scalar_func = new Function(...this.args_keys, ...this.fields, "$acc", '"use strict";\n'+this.func)
    this.change.emit()
  }

  compute(x: any[]){
    return this.scalar_func!(...this.args_values, ...x)
  }

  update_vfunc(){
    this.args_keys = Object.keys(this.parameters)
    this.args_values = Object.values(this.parameters)
    this.vector_func = new Function(...this.args_keys, ...this.fields, "data_source", "$initial_state",'"use strict";\n'+this.v_func)
    this.change.emit()
  }

  update_args(){
    this.args_keys = Object.keys(this.parameters)
    this.args_values = Object.values(this.parameters)
    this.change.emit()
  }

  v_compute(xs: any[], data_source: any, initial_state: any = 0){
      if(this.vector_func){
        return this.vector_func(...this.args_values, ...xs, data_source, initial_state)
      } else if(this.scalar_func){
        let acc = initial_state
        let l = xs.length > 0 ? xs[0].length : data_source.get_length()
        let xs_local = Array(xs.length)
        for(let i=0; i<l; i++){
          for(let j=0; j<xs.length; j++){
            xs_local[j] = xs[j][i]
          }
          acc = this.scalar_func(...this.args_values, ...xs_local, acc)
        }
        return acc
      } else {
        return null
      }
  }

}
