import {Model} from "model"
import {ColumnarDataSource} from "models/sources/columnar_data_source"
import * as p from "core/properties"

export namespace ClientLinearFitter {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Model.Props & {
    fields: p.Property<Array<string>>
    source: p.Property<ColumnarDataSource>
    varY: p.Property<string>
    weights: p.Property<string|null>
    eps: p.Property<number>
  }
}

// Cholesky decomposition without pivoting - inplace
// TODO: Perhaps add a version with pivoting too?
function chol(X: number[], nRows: number){
  let iRow = 0
  let jRow, kRow
  for(let i=0; i<nRows; ++i){
    iPivot = i
    pivotDiag = 1/X[i+iRow]
    jRow = iRow+i+1
    for(let j=i+1; j<nRows; ++j) {
      pivotRow = pivotDiag*X[i+jRow]
      kRow = iRow+i+1
      for(let k=i+1; k<=j; ++k){
	X[k+jRow] -= pivotRow*X[i+kRow]
	kRow += k+1
      }
      for(let k=j+1; k<nRows; ++k) {
	X[j+kRow] -= pivotRow*X[i+kRow]
	kRow += k+1
      }
      X[i+jRow] = pivotRow
      jRow += j+1
    }
    iRow += i+1
  }
  return X
}

// Solves a system of linear equations using Cholesky decomposition
function solve(x:number[], y:number[]){
  let nRows = y.length
  chol(x,nRows)
  iRow = 0
  for(let i=0; i<nRows; ++i){
    for(let j=0; j<i; ++j){
      y[i] -= y[j]*x[iRow+j]
    }
    iRow += i+1
  }
  let iDiag=0
  for(let i=0; i<nRows; i++){
    y[i] /= x[iDiag]
    iDiag += i+2
  }
  let jRow = 0
  for(let i=nRows-1; i>=0; --i){
    jRow = 1+((x*(x+5))>>1)
    for(let j=i+1; j<nRows; ++j){
      y[i] -= y[j]*x[jRow]
      jRow += j+1
    }
  }
  return y
}

export interface ClientLinearFitter extends ClientLinearFitter.Attrs {}

export class ClientLinearFitter extends Model {
  properties: ClientLinearFitter.Props

  constructor(attrs?: Partial<ClientLinearFitter.Attrs>) {
    super(attrs)
  }

  static __name__ = "ClientLinearFitter"

  static init_ClientLinearFitter() {
    this.define<ClientLinearFitter.Props>(({Array, String, Number})=>({
      fields: [Array(String), []],
      source: [Ref(ColumnarDataSource)],
      eps: [Number, 0],
      varY: [String],
      weights: [String, null]
    }))
  }

  initialize(){
    super.initialize()
    this._lock = false
    this.fit()
  }

  args_keys: Array<string>
  args_values: Array<any>

  _lock: bool

  parameters: Array<number>

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.source.change, this.onChange)
  }

  onChange(){
    if(this._lock){
      return
    }
    this._lock = true
    this.fit()
    this.change.emit()
    this._lock = false
  }

  fit(){
    let x = []
    for(let i=0; i<this.fields.length; ++i){
      let iField = this.source.get_column(fields[i])
      for(let j=0; j<=i; ++j){
	let acc = 0
	let jField = this.source.get_column(this.fields[j])
	// HACK: for some reason ES6 reduce eats too much memory
	for(let k=0; k<iField.length; ++k){
	  acc += iField[k]*jField[k]
	}
	x.push(acc)
      }
    }
    this.parameters = []
    const colY = this.source.get_column(this.varY)
    for(let i=0; i<this.fields.length; ++i){
      let col = this.source.get_column(iField)
      x.push(col.reduce((acc, cur) => acc+cur, 0))
      let acc = 0
      for(let k=0; k<col.length; k++){
	acc += col[k]*varY[k]
      }
      this.parameters.push(acc)
    }
    x.push(this.source.get_length())
    this.parameters.push(colY.reduce((acc, cur)=>acc+cur,0))
    solve(x,this.parameters)
  }

  v_compute(xs: any[], data_source: any, output: any[] | null =null){
    if(xs.length + 1 !== this.parameters.length){
      throw Exception("Invalid number of parameters, expected " + this.parameters.length + " got " + xs.length)
    }
    if(output != null && output.length === data_source.get_length()){
      output.fill(this.parameters[xs.length])
      for(let i=0; i<xs.length; i++){
	let x = xs[i]
	for(let j=0; j<x.length; ++j){
	  output[j] += x[j]*this.parameters[i]
	}
      } 
    } 
    return output
  }

}
