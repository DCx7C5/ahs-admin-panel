import React, {RefObject, useCallback, useEffect, useRef} from "react";
import {inspectFunction} from "../components/utils";


interface AHSCommandInput {
  webSocketIns: WebSocket,
  uniqueId: string,
  javaScriptFunction?: CallableFunction,
}

interface AHSCommand {
  func_name: string,
  func_args: Array<any>,
  func_kwargs: object,
  unique_id: string,
  timestamp: number,
  send: () => void,
  register: () => void,
  callback: () => void,
}


const _parseCommandNameFromJSCallable = (jsCommand: CallableFunction): string => {
  return jsCommand.name.replace(/([a-z])([A-Z])/g, '$1_$2').toLowerCase()
}


export const useAHSCommand = ({webSocketIns, uniqueId, javaScriptFunction}: AHSCommandInput): AHSCommand => {
  const command = useRef({
    func_name: '',
    func_args: [],
    func_kwargs: {},
    unique_id: uniqueId,
    timestamp: Date.now(),
    send: () => _sendCommand(webSocketIns),
    register: () => _registerCommand(),
  }).current;

  useEffect(() => {
    if (!command.func_name) return;
    console.log('Creating and register AHS command')

    return () => {
      console.log('Cleaning up AHS command: ', command.func_name)
    }
  }, [])

  const _sendCommand = useCallback((webSocketIns) => {
      webSocketIns.send(JSON.stringify({
        "type": "command",
        "data": command,
      }))
  }, []);

  const _registerCommand = useCallback(() => {

  }, [])

  function _serializeCommand() {
    return JSON.stringify(command)
  }

  function _deserializeCommand() {

    return JSON.parse()
  }

  function _fromFunction(javaScriptFunction: CallableFunction) {
    const commandName = _parseCommandNameFromJSCallable(javaScriptFunction)

    return _serializeCommand()
  }

  function _fromSocket() {

  }


  function _inspectCommand() {
    return
  }

  return command
}



export default useAHSCommand;
