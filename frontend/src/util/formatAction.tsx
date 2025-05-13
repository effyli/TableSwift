import { Action } from "../types/action";

export const formatLabelsJson = (action: Action) => { 
// Make the label items json
if (action.descriptions) {
    action.descriptions.forEach(desc => {
        if (desc.labels) {
            desc.labels = {
                ...desc.labels,
                json: JSON.stringify(desc.labels)
            };
        }
    });
}
return action;
}