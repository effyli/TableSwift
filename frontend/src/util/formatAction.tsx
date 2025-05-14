import { Action } from "../types/action";

export const formatActionJson = (action: Action) => { 
    // Make the label items json
    if (action.descriptions) {
        action.descriptions.forEach(desc => {
            if (desc.labels) {
                desc.labels = desc.labels.map(label => ({
                    ...label,
                    json: JSON.stringify(label.json)
                }));
            }
        });
    }
    return action;
}