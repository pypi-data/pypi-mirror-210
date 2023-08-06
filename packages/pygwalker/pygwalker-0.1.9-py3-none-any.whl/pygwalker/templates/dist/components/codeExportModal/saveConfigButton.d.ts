import React from "react";
interface IDsaveConfigButtonProps {
    sourceCode: string;
    configJson: any;
    setPygCode: (code: string) => void;
    setTips: (tips: string) => void;
}
declare const saveConfigButton: React.FC<IDsaveConfigButtonProps>;
export default saveConfigButton;
