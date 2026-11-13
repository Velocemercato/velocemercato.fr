import payload from './payload.mjs';
import landing from './landing.mjs';
import {createHandler} from './core.mjs';
export {Consultation} from './core.mjs';
export default createHandler(payload,landing);
