import { Id, Data, Pin, Wire, Component, Readable, Writeable } from './types'

export abstract class AbstractPin implements Pin {
  private _id: Id
  protected _source: Component
  protected _wires: Set<Wire>

  protected _data: number
  protected _bandwidth: number

  protected constructor(id: Id, source: Component, bandwidth = 1, data = 0) {
    this._id = id
    this._source = source
    this._wires = new Set<Wire>()
    this._data = data
    this._bandwidth = bandwidth
  }

  public get id(): Id | undefined {
    return this._id
  }

  public get source(): Component {
    return this._source
  }

  public get wires(): Wire[] {
    return [...this._wires]
  }

  // public get data(): number {
  //     return this._data;
  // }

  // protected set data(data: number) {
  //     if (!this.validate(data))
  //         throw new RangeError(`data should be between 0 and ${(Math.pow(2, this._bandwidth) - 1)}.`)
  //     this._data = data
  // }

  protected validate(data: number) {
    return Math.log2(data) < this._bandwidth
  }

  public attach(wire: Wire, delay = 0): void {
    this._wires.add(wire)
  }

  public detach(wire: Wire): void {
    this._wires.delete(wire)
  }

  public update(wire: Wire, data: Data): void {
    let updated = this._data !== data
    this._data = data
    if (updated) this._source.update()
  }
}


export class ReadonlyPin extends AbstractPin implements Readable {
  public attach(wire: Wire, delay = 0): void {
    super.attach(wire, delay)
    wire.addConsumer(this, delay)
  }

  public detach(wire: Wire): void {
    super.detach(wire)
    wire.removeConsumer(this)
  }

  public read(): Data {
    return this._data
  }
}

export class WriteonlyPin extends AbstractPin implements Writeable {
  public attach(wire: Wire, delay = 0): void {
    super.attach(wire, delay)
    wire.addSupplier(this, delay)
  }

  public detach(wire: Wire): void {
    super.detach(wire)
    wire.removeSupplier(this)
  }

  public write(data: Data): void {
    let updated = this._data !== data
    this._data = data
    if (updated)
      this._wires.forEach(wire => wire.supply(this, this._data))
  }
}