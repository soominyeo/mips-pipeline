import { PinError } from "../component/errors";
import { Data, Pin, Unit, Wire } from "../component/types";
import { CircuitEvent } from "./types";

export abstract class AbstractEvent<S extends Unit, D extends Unit> implements CircuitEvent<S, D> {
    protected readonly _source: S;
    protected readonly _dest: D;

    protected constructor(source: S, dest: D) {
        this._source = source
        this._dest = dest
    }

    public get source(): S {
        return this._source
    }

    public get dest(): D {
        return this._dest
    }

    public abstract execute(): CircuitEvent<S, D>

    public abstract rollback(): CircuitEvent<S, D>
}

export abstract class TransmitEvent<S extends Unit, D extends Unit> extends AbstractEvent<S, D> {
    protected data: Data

    public constructor(source: S, dest: D, data: Data) {
        super(source, dest)
        this.data = data
    }
}

export class WireTransmitEvent extends AbstractEvent<Wire, Pin>