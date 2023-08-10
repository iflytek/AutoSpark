import React, {useState, useEffect, useRef} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {getOrganisationConfig, updateOrganisationConfig, validateLLMApiKey} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {removeTab, setLocalStorageValue} from "@/utils/utils";
import Image from "next/image";

export default function Settings({organisationId}) {
    const [modelApiKey, setKey] = useState('');
    const [modelApiSecret, setApiSecret] = useState('');
    const [modelAppId, setAppId] = useState('');


    const [temperature, setTemperature] = useState(0.5);
    const [sourceDropdown, setSourceDropdown] = useState(false);
    const [source, setSource] = useState('OpenAi');
    const sourceRef = useRef(null);
    const sources = ['OpenAi', 'Google Palm', 'SparkAI']
    const [isSparkAI, setIsSpark] = useState(false);

    function getKey(key) {
        getOrganisationConfig(organisationId, key)
            .then((response) => {
                setKey(response.data.value);
                if (response.data.value ==="SparkAI") {
                    setIsSpark(true);
                }
            })
            .catch((error) => {
                console.error('Error fetching project:', error);
            });
    }

    function getSource(key) {
        getOrganisationConfig(organisationId, key)
            .then((response) => {
                setSource(response.data.value);
                setIsSpark(true)
            })
            .catch((error) => {
                console.error('Error fetching project:', error);
            });
    }

    useEffect(() => {
        getKey("model_api_key");
        getKey("model_api_secret");
        getKey("model_app_id");

        getSource("model_source");

        function handleClickOutside(event) {
            if (sourceRef.current && !sourceRef.current.contains(event.target)) {
                setSourceDropdown(false);
            }
        }

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [organisationId]);

    function setLocalStorageIsSpark(source) {
        if (source === "SparkAI") {
            localStorage.setItem("is_spark", "true")
        } else {
            localStorage.setItem("is_spark", "false")
        }
    }

    function updateKey(key, value) {
        const configData = {"key": key, "value": value};
        return updateOrganisationConfig(organisationId, configData)
            .then((response) => {
                return response.data;
            })
            .catch((error) => {
                console.error('Error updating settings:', error);
                throw new Error('Failed to update settings');
            });
    }

    const handleModelApiKey = (event) => {
        setKey(event.target.value);
    };

    const handleModelApiSecret = (event) => {
        setApiSecret(event.target.value);
    };

    const handleSparkModelAppId = (event) => {
        setAppId(event.target.value);
    };
    const handleSourceSelect = (index) => {
        setSource(sources[index]);
        setSourceDropdown(false);
        if (sources[index] == "SparkAI") {
            setIsSpark(true);
        }else {
            setIsSpark(false);
        }
    };

    const saveSettings = () => {
        if (modelApiKey === null || modelApiKey.replace(/\s/g, '') === '') {
            toast.error("API key is empty", {autoClose: 1800});
            return;
        }
        // spark check
        if (modelApiSecret === null || modelApiSecret.replace(/\s/g, '') === '') {
        }
        if (modelAppId === null || modelAppId.replace(/\s/g, '') === '') {
        }

        validateLLMApiKey(source, modelApiKey, modelApiSecret, modelAppId)
            .then((response) => {
                if (response.data.status === "success") {
                    Promise.all([
                        updateKey("model_api_key", modelApiKey),
                        updateKey("model_api_secret", modelApiSecret),
                        updateKey("model_app_id", modelAppId),
                        updateKey("model_source", source),
                        setLocalStorageIsSpark(source)

                    ])
                        .then(() => {
                            toast.success("Settings updated", {autoClose: 1800});
                        })
                        .catch((error) => {
                            console.error('Error updating settings:', error);
                            toast.error("Failed to update settings", {autoClose: 1800});
                        });
                } else {
                    toast.error("Invalid API Access key", {autoClose: 1800});
                }
            })
            .catch((error) => {
                console.error('Error validating API key:', error);
                toast.error("Failed to validate API key", {autoClose: 1800});
            });
    };

    const handleTemperatureChange = (event) => {
        setTemperature(event.target.value);
    };

    return (<>
        <div className="row">
            <div className="col-3"></div>
            <div className="col-6" style={{overflowY: 'scroll', height: 'calc(100vh - 92px)', padding: '25px 20px'}}>
                <div>
                    <div className={agentStyles.page_title}>Settings</div>
                </div>
                <div>
                    <label className={agentStyles.form_label}>Model Source</label>
                    <div className="dropdown_container_search" style={{width: '100%'}}>
                        <div className="custom_select_container" onClick={() => setSourceDropdown(!sourceDropdown)}
                             style={{width: '100%'}}>
                            {source}<Image width={20} height={21}
                                           src={!sourceDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'}
                                           alt="expand-icon"/>
                        </div>
                        <div>
                            {sourceDropdown &&
                                <div className="custom_select_options" ref={sourceRef} style={{width: '100%'}}>
                                    {sources.map((source, index) => (
                                        <div key={index} className="custom_select_option"
                                             onClick={() => handleSourceSelect(index)}
                                             style={{padding: '12px 14px', maxWidth: '100%'}}>
                                            {source}
                                        </div>))}
                                </div>}
                        </div>
                    </div>
                </div>
                <br/>
                <div>
                    <label className={agentStyles.form_label}>SparkAI(星火)/Open-AI/Palm API Key</label>
                    <input placeholder="Enter your SparkAI/Open-AI/Palm API key" className="input_medium"
                           type="password"
                           value={modelApiKey} onChange={handleModelApiKey}/>
                </div>
                { isSparkAI?(
                                    <div>

                    <label className={agentStyles.form_label}>SparkAI(星火) API Secret</label>
                    <input placeholder="Enter your Api Secret If you it need" className="input_medium" type="password"
                           value={modelApiSecret} onChange={handleModelApiSecret}/>
                </div>):null}
                { isSparkAI?(
                <div>
                    <label className={agentStyles.form_label}>SparkAI(星火) APP ID</label>
                    <input placeholder="Enter your SparkAI APP ID" className="input_medium" type="password"
                           value={modelAppId} onChange={handleSparkModelAppId}/>
                </div>):null}

                {/*<div style={{marginTop:'15px'}}>*/}
                {/*  <label className={agentStyles.form_label}>Temperature</label>*/}
                {/*  <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>*/}
                {/*    <input style={{width:'89%'}} type="range" step={0.1} min={0} max={1} value={temperature} onChange={handleTemperatureChange}/>*/}
                {/*    <input style={{width:'9%',order:'1',textAlign:'center',paddingLeft:'0',paddingRight:'0'}} disabled={true} className="input_medium" type="text" value={temperature}/>*/}
                {/*  </div>*/}
                {/*</div>*/}
                <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '15px'}}>
                    <button onClick={() => removeTab(-3, "Settings", "Settings", 0)} className="secondary_button"
                            style={{marginRight: '10px'}}>
                        取消
                    </button>
                    <button className="primary_button" onClick={saveSettings}>
                        更新
                    </button>
                </div>
            </div>
            <div className="col-3"></div>
        </div>
        <ToastContainer/>
    </>)
}
