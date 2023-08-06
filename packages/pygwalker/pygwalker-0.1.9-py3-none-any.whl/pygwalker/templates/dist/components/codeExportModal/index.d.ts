import React from "react";
interface ICodeExport {
    globalStore: any;
    sourceCode: string;
    open: boolean;
    setOpen: (open: boolean) => void;
}
declare const CodeExport: React.FC<ICodeExport>;
export default CodeExport;
