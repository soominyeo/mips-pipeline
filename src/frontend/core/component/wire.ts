import { WireError } from "./errors";
import { Id, Pin, Wire } from "./types";

export class AbstractWire implements Wire {
    private _id: Id
    protected _baseDelay: number
    protected _delayMap: Map<Pin, number>
    protected _suppliers: Set<Pin>
    protected _consumers: Set<Pin>

    protected constructor(id: Id, baseDelay = 0) {
        this._id = id
        this._baseDelay = baseDelay
        this._delayMap = new Map<Pin, number>()
        this._suppliers = new Set<Pin>()
        this._consumers = new Set<Pin>()
    }

    public getDelay(pin: Pin): number {
        let delay = this._delayMap.get(pin) 
        if (delay === undefined)
            throw new WireError()
        return delay
    }

    public setDelay(pin: Pin, delay: number): void {
        this._delayMap.set(pin, delay)
    }

    public supply(supplier: Pin, data: number): void {
        if (!this._suppliers.has(supplier))
        
            supplier.update(this, data)
    }

    public addSupplier(supplier: Pin, delay: number = 0): void {
        this._suppliers.add(supplier)
        this._delayMap.set(supplier, delay)
    }

    public addConsumer(consumer: Pin, delay: number = 0): void {
        this._consumers.add(consumer)
        this._delayMap.set(consumer, delay)
    }

    public removeSupplier(supplier: Pin): void {
        this._suppliers.delete(supplier)
        this._delayMap.delete(supplier)
    }

    public removeConsumer(consumer: Pin): void {
        this._consumers.delete(consumer)
        this._delayMap.delete(consumer)
    }
}