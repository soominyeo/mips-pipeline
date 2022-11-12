export type Id = string | number | [string, number]
export type Data = number

export interface Unit {
    readonly id?: Id;
}


export interface Linkable {
    
}

/**
 * Represents a wire connecting each output pins and input pins.
 * Works as a subject in a Publisher-subsriber pattern.
 * Maintains a scheduling queue.
 */
 export interface Wire extends Unit, Linkable {
    delay: number;
    supply(supplier: Pin, data: Data): void;
    addSupplier(supplier: Pin, delay?: number): void;
    addConsumer(consumer: Pin, delay?: number): void;
    removeSupplier(supplier: Pin): void;
    removeConsumer(consumer: Pin): void;
}


/**
 * Represents a interface between a component and a wire.
 * Works as either publisher or subscriber, or even both in a Publisher-subsriber pattern.
 */
export interface Pin extends Unit {
    readonly source: Component;
    readonly wires: Wire[];

    attach(wire: Wire, delay?: number): void;
    detach(wire: Wire): void;
    update(wire: Wire, data: Data): void;
}

export interface Readable {
    read(): Data;
}


export interface Writeable {
    write(data: Data): void;
}



export interface Component extends Unit {
    readonly pin: { [id: string | number]: Pin };
    update(pin?: Pin): void;
}


export interface Circuit extends Component {
    horSize: Number;
    vertSize: Number;
    components: Component[];
    getPosition(sub: Component | Pin): [Number, Number];
    setPosition(sub: Component | Pin, pos: [Number, Number]): void;
}