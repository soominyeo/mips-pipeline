import { Id, Pin, Component } from "./types"


export abstract class AbstractPin implements Pin {
    private _id: Id;
    private _source: Component;

    private _data: number;
    private _bandwidth: number;



    protected constructor(id: Id, source: Component, bandwidth = 1, data = 0) {
        this._id = id;
        this._source = source;
        this._mapped = new Set()
        this._data = 0;
        this._bandwidth = bandwidth;

    }

    public get id(): Id | undefined {
        return this._id;
    }

    public get source(): Component {
        return this._source;
    }

    public abstract get mapped(): Set<Pin>;

    public get data(): number {
        return this._data ? this._data : 
    }

    protected set data(data: number) {
        if (!this.validate(data))
            throw new RangeError(`data should be between 0 and ${(Math.pow(2, this._bandwidth) - 1)}.`)
        this._data = data
    }

    protected validate(data: number) {
        return Math.log2(data) < this._bandwidth
    }

    public attach(pin: Pin): void {
        this.mapped.add(pin)
    }

    public detach(pin: Pin): void {
        this.mapped.delete(pin)
    }
}