export type Id = string | number | [string, number]

/**
 * Represents a interface between a component and a wire.
 * Works as either publisher or subscriber, or even both in a Publisher-subsriber pattern.
 */
export interface Pin {
    readonly id: Id | undefined;
    readonly source: Component;
    readonly wire: Wire;
    readonly data: number;
    
    attach(pin: Pin): void;
    detach(pin: Pin): void;
    update(): void; 
    read?(): number;
    write?(data: number): void;
}

/**
 * Represents a wire connecting each output pins and input pins.
 * Works as a subject in a Publisher-subsriber pattern.
 * Maintains delayed
 */
export interface Wire {
    supply(): void;
    
    addSupplier(supplier: Pin): void;
    addConsumer(consumer: Pin): void;
    removeSupplier(supplier: Pin): void;
    removeConsumer(consumer: Pin): void;
}


export interface Component {
    readonly id?: Id;
    readonly pin: { [id: string | number]: Pin };
    update(): void;
}


export interface CircuitComponent extends Component {
    pinins(): Pin[];
    pinouts(): Pin[];
}