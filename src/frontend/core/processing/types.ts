import { Unit } from "../component/types"

export type Schedule = {
    time: BigInteger
    event: CircuitEvent<?,?>
}

export interface CircuitEvent<S extends Unit, D extends Unit> {
    readonly source: S
    readonly dest: D
    execute(): CircuitEvent<S, D>
    rollback(): CircuitEvent<S, D>
}

export interface Queue {
    keepHistory: boolean;
    schedule(event: CircuitEvent<?, ?>, delay: number): Schedule;
    schedule(event: CircuitEvent<?, ?>, time: BigInt): Schedule;
    // schedule(event: QueueEvent, x: number | BigInt): Schedule;
    advance(diff: number): void;
    retreat(diff: number): void;
    jump(time: BigInt): void;
}

export interface Context