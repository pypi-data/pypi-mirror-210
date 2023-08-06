class aib_logger:
    from enum import Enum
    
    class Categories(Enum):
        MODEL="Model"
        DATA="Data"
        METRIC="Metric"
        OTHER="Other"

    class Actions(Enum):
        CREATE="Create"
        UPDATE="Update"
        DELETE="Delete"
        UPLOAD="Upload"
        MODEL_SCORE="Model_Score"
        DATA_STAT="Data_statistics"
        OTHER="Other"
    
    class Severities(Enum):
        INFO="INFO"
        WARNING="WARNING"
        ERROR="ERROR"

    def __init__(
        self, 
        project:str, 
        region:str,
        pipeline_name:str="", 
        logger_name:str="aib_custom_logger",
        ):
        """
        This class use to add custom logs for vertex AI.
        class initialization with given project and pipeline name.

        ...
        Methods:
        log(): to log basic info of pipeline/component status
        model_logs(): to log model performance score in custom logs.
        data_stat_log(): to log data statistic in custom logs.
        ...

        Args:
            project(str): project id where your vertex AI pipeline running
            region(str): Region of pipeline
            pipeline_name(str): name of pipeline
            logger_name(str): name of custom logger 
                (default is aib_custom_logger)
        Returns:
            None
        """
        import logging
        import google.cloud.logging
        self.project=project
        self.region=region
        self.pipeline_name=pipeline_name
        client = google.cloud.logging.Client(project=project)
        self.logger = client.logger(name=logger_name)

    def log(
        self,
        msg:str,
        status:str='',
        clock_time:float=0.0,
        process_time:float=0.0,
        severity:Severities=Severities.INFO,
        ):
        """
        Log basic information of pipeline and component.
        Args:
            msg(str): message to add in logs
            status(str): status of component
                default is empty string
            clock_time(float): add time taken by function/component
                default is 0.0
            process_time(float): add CPU time taken by function/component
                default is 0.0
            severity(str): default is INFO
        Returns:
            None
        """
        import inspect
        import time
    
        t_time = time.time()
        payload={
            "pipeline_run_name":self.pipeline_name,
            "region":self.region,
            "project":self.project,
            "component_name": inspect.stack()[1].function,
            "status":status,
            "time":t_time,
            "duration":clock_time,
            "process_time":process_time,
            "message":msg,
        }
        self.logger.log_struct(payload, severity=severity.value)

    
    def model_log(
        self,
        msg:str,
        category:Categories=Categories.MODEL,
        action:Actions=Actions.MODEL_SCORE,
        severity:Severities=Severities.INFO,
        model_name:str="AIB_Test",
        model_version:str="default",
        data_subset:str='training',
        model_type:str='regression',
        accuracy_score:float=0.00,
        confusion_metric:dict={'TP':0,'TN':0,'FP':0,'FN':0},
        precision:float=0.00,
        recall:float=0.00,
        f1_score:float=0.00,
        roc_auc_score:float=0.00,
        precision_recall_auc:float=0.00,
        log_loss:float=0.00,
        zero_one_loss_normal:float=0.00,
        zero_one_loss_fraction:float=0.00,
        balanced_accuracy_score_normal:float=0.00,
        balanced_accuracy_score_adjusted:float=0.00,
        brier_score_loss:float=0.00,
        brier_score_loss_0_positive:float=0.00,
        fbeta_precision:float=0.00,
        fbeta_score_recall:float=0.00,
        hamming_loss:float=0.00,
        r2_score:float=0.00,
        mean_absolute_error:float=0.00,
        mean_squared_error:float=0.00, 
        mean_squared_log_error:float=0.00,
        median_absolute_error:float=0.00,
        explained_variance_score:float=0.00,
        residual_error:float=0.00,
        adjusted_rand_score:float=0.00,
        extra_labels:list=[],
        object:dict={},
        **kwargs
    ):
        """
        Method to add model state and performace score in logs, all arguments are set to 
        default 0.00 (type float)
        
        example:
        from aib_logging.logger import aib_logger
        logger = aib_logger("my-gcp-project-name",pipeline_name="pipeline_job_name")
    
        logger.model_log(
            "This is test for model score",
            model_name="sklearn_model",
            model_version="champion",
            data_subset="training",
            model_type="classification",
            accuracy_score=78.5275893,
            )

        Args:
            msg:str,
            category: Categories of log type 
                default is model,
            action: Actions perform for logs 
                default is model_score,
            severity: Severities for logs,
                default is INFO
            model_name(str): Name of model 
                default is 'AIB_Test',
            model_version(str): model version
                default is 'default'
            data_subset(str): type of your data set/sample (training,validation,test)
                default is training
            model_type(str): type of model (regression,classification,clustering)
                default is regression
            model score metrics get selected on basis of model type. 
                model_type = 'classification'
                    accuracy_score:float=0.00,
                    confusion_metric:dict={'TP':0,'TN':0,'FP':0,'FN':0},
                    precision:float=0.00,
                    recall:float=0.00,
                    f1_score:float=0.00,
                    roc_auc_score:float=0.00,
                    precision_recall_auc:float=0.00,
                    log_loss:float=0.00,
                    zero_one_loss_normal:float=0.00,
                    zero_one_loss_fraction:float=0.00,
                    balanced_accuracy_score_normal:float=0.00,
                    balanced_accuracy_score_adjusted:float=0.00,
                    brier_score_loss:float=0.00,
                    brier_score_loss_0_positive:float=0.00,
                    fbeta_precision:float=0.00,
                    fbeta_score_recall:float=0.00,
                    hamming_loss:float=0.00,
                model_type = 'regression'
                    r2_score:float=0.00,
                    mean_absolute_error:float=0.00,
                    mean_squared_error:float=0.00, 
                    mean_squared_log_error:float=0.00,
                    median_absolute_error:float=0.00,
                    explained_variance_score:float=0.00,
                    residual_error:float=0.00,
                model_type = 'clustering'
                    adjusted_rand_score:float=0.00,
                    accuracy_score:float=0.00,
                    confusion_metric:dict={'TP':0,'TN':0,'FP':0,'FN':0},
            extra_labels:list=[],
            object:dict={},
            **kwargs

        Retuns:
            None
        """
        import inspect
        
        if model_type == 'classification':
            payload={
                "pipeline_run_name":self.pipeline_name,
                "component_name": inspect.stack()[1].function,
                "project":self.project,
                "region":self.region,
                "category":category.value,
                "action":action.value,
                "model_name":model_name,
                "model_version":model_version,
                "data_subset":data_subset,
                "model_type":model_type,
                "accuracy_score":accuracy_score,
                "confusion_metric":confusion_metric,
                "precision":precision,
                "recall":recall,
                "f1_score":f1_score,
                "roc_auc_score":roc_auc_score,
                "precision_recall_auc":precision_recall_auc,
                "log_loss":log_loss,
                "zero_one_loss_normal":zero_one_loss_normal,
                "zero_one_loss_fraction":zero_one_loss_fraction,
                "balanced_accuracy_score_normal":balanced_accuracy_score_normal,
                "balanced_accuracy_score_adjusted":balanced_accuracy_score_adjusted,
                "brier_score_loss":brier_score_loss,
                "brier_score_loss_0_positive":brier_score_loss_0_positive,
                "fbeta_precision":fbeta_precision,
                "fbeta_score_recall":fbeta_score_recall,
                "hamming_loss":hamming_loss,
                "extra_labels":extra_labels,
                "message":msg,
                "object":object
            }
            for key, value in kwargs.items():
                payload[key]=value
        
        if model_type == 'regression':
            payload={
                "pipeline_run_name":self.pipeline_name,
                "component_name": inspect.stack()[1].function,
                "project":self.project,
                "region":self.region,
                "category":category.value,
                "action":action.value,
                "model_name":model_name,
                "model_version":model_version,
                "data_subset":data_subset,
                "model_type":model_type,
                "r2_score":r2_score,
                "mean_absolute_error":mean_absolute_error,
                "mean_squared_error":mean_squared_error,
                "mean_squared_log_error":mean_squared_log_error,
                "median_absolute_error":median_absolute_error,
                "explained_variance_score":explained_variance_score,
                "residual_error":residual_error,                
                "extra_labels":extra_labels,
                "message":msg,
                "object":object
            }
            for key, value in kwargs.items():
                payload[key]=value
        
        if model_type == 'clustering':
            payload={
                "pipeline_run_name":self.pipeline_name,
                "component_name": inspect.stack()[1].function,
                "project":self.project,
                "region":self.region,
                "category":category.value,
                "action":action.value,
                "model_name":model_name,
                "model_version":model_version,
                "data_subset":data_subset,
                "model_type":model_type,
                "accuracy_score":accuracy_score,
                "confusion_metric":confusion_metric,
                "adjusted_rand_score":adjusted_rand_score,
                "extra_labels":extra_labels,
                "message":msg,
                "object":object
            }
            for key, value in kwargs.items():
                payload[key]=value
                
        self.logger.log_struct(payload, severity=severity.value)

    def data_stat_log(
        self,
        msg:str,
        category:Categories=Categories.DATA,
        action:Actions=Actions.DATA_STAT,
        severity:Severities=Severities.INFO,
        min_val:dict={},
        max_val:dict={},
        mean_val:dict={},
        std_val:dict={},
        count_val:dict={},
        percentile_25:dict={},
        percentile_50:dict={},
        percentile_75:dict={},
        unique:dict={},
        top:dict={},
        freq:dict={},
        extra_labels:list=[],
        object:dict={},
        **kwargs
        ):
        """
        Method to log data statistic into logs

        example:
        from aib_logging.logger import aib_logger
        logger = aib_logger("my-gcp-project-name",pipeline_name="pipeline_job_name")
    
        logger.data_stat_log(
            "This is test for data statistics",
            min={'col1':0.00,'col2':0.00...}.
            max={'col1':77.00,'col2':100.00...},
            count={'col1':1000,'col2':10000...},
            )

        Args:
            msg:str,
            category: Categories of log type 
                default is model,
            action: Actions perform for logs 
                default is model_score,
            severity: Severities for logs,
                default is INFO
            min_val(dict): min value of dataset column in key,value pair
                default is empty dict {}
            max_val(dict) maximum value of dataset column in key,value pair
                default is empty dict {},
            mean_val(dict): mean value of dataset column in key,value pair
                default is empty dict {},
            std_val(dict): standard deviation value of dataset column in key,value pair,
                default is empty dict {},
            count_val(dict): values count of dataset column in key,value pair
                default is empty dict {},
            percentile_25(dict): 25% value of dataset column in key,value pair
                default is empty dict {},
            percentile_50(dict): 50% value of dataset column in key,value pair
                default is empty dict {},
            percentile_75(dict): 75% value of dataset column in key,value pair
                default is empty dict {},
            unique(dict): unique values for categorical column
                default is empty dict {},
            top(dict): top value for categorical column
                default is empty dict {},
            freq(dict): frequency of value in categorical column
                default is empty dict {},
            extra_labels:list=[],
            object:dict={},
            **kwargs
        """
        import inspect
        payload={
            "pipeline_run_name":self.pipeline_name,
            "component_name": inspect.stack()[1].function,
            "project":self.project,
            "region":self.region,
            "category":category.value,
            "action":action.value,
            "min":min_val,
            "max":max_val,
            "count":count_val,
            "mean":mean_val,
            "std":std_val,
            "percentile_25":percentile_25,
            "percentile_50":percentile_50,
            "percentile_75":percentile_75,
            "unique":unique,
            "top":top,
            "freq":freq,
            "extra_labels":extra_labels,
            "message":msg,
            "object":object
        }
        for key, value in kwargs.items():
                payload[key]=value
        # Send the Log request
        self.logger.log_struct(payload, severity=severity.value)