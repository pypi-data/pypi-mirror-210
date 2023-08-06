"""
LetsScrape, email: hello@letsscrape.com
"""
import asyncio
import time
from typing import List, Optional, Union, Dict, AnyStr
from urllib.parse import urlencode
from purl import URL

import aiohttp

from schemas.basic_domain_data import SimilarWebBasicDomainDataModel
from schemas.complete_data_task import SimilarWebCompleteDataTaskModel
from schemas.task import SimilarWebTaskResultModel
from schemas.task_status import TaskStatus
from schemas.my_tasks import SimilarWebMyTasksModel
from schemas.cancel_task import SimilarWebCancelTaskModel
from logger_mock import SimilarWebLoggerMock
 

class SimilarWebRapidAPI(object):
    def __init__(self, rapid_api_key: AnyStr, logger = None):
        """
        To get rapid_api_key you just have to register here https://bit.ly/3Mz1U9n
        :param rapidapi_host: X-RapidAPI-Host header & Base URL
        :param rapidapi_key: X-RapidAPI-Key header
        """

        self.rapidapi_host = 'similarweb-working-api.p.rapidapi.com'
        self.logger = SimilarWebLoggerMock() if logger is None else logger
        self.headers = {
            "X-RapidAPI-Key": rapid_api_key,
            "X-RapidAPI-Host": self.rapidapi_host,
        }


    async def __get_request(self, path: AnyStr, params: Optional[Dict] = None) -> Dict:
        """
        :param path: Request path
        :param params: Request query parameters
        :return: JSON Response Dictionary
        """

        if params:
            query_string = urlencode(params)
        else:
            query_string = ""

        url = URL(
            host=self.rapidapi_host,
            path=path,
            query=query_string,
            scheme="https"
        ).as_string()
        print(url)
        session_timeout = aiohttp.ClientTimeout(total=45.0)
        is_ok = False

        while True:
            async with aiohttp.ClientSession(headers=self.headers, timeout=session_timeout) as session:
                async with session.get(url=url) as response:
                    try:
                        json_response = await response.json()  
                        if response.status == 200:  
                            is_ok = True
                    except aiohttp.client.ContentTypeError:
                        continue
                    if is_ok:
                        break
            await asyncio.sleep(0.3)

        return json_response
    
    async def __wait(self):
        await asyncio.sleep(1)

    async def get_basic_data_from_domain(self, domain: str) -> List[
        SimilarWebBasicDomainDataModel]:
        """
        Gets basic domain data from SimilarWeb. You will receive from this endpoint 
        data like: top country shares, monthly visits, user engagements, ranks and traffic 
        sources. In many cases such data meet the clients needs. If you want complete
        domain data check get_complete_data_task out!
        """

        path = f"/similarweb/getdata?domain={domain}"
        response_data = await self.__get_request(path=path)
        response = SimilarWebBasicDomainDataModel.parse_obj(response_data)
        return response
    
    
    async def get_complete_data_for_domain(self, domain:str, callback_url:str = "") -> SimilarWebTaskResultModel:
        """
        Instead of using get_complete_data_task and then downloading get task result 
        use this method. It'll do everything for you.
        """
        user_task = await self.get_complete_data_task(domain, callback_url)
        task_result = None

        while True:
            await self.__wait()
            task_result = await self.get_task_result(user_task.data.task_id)

            if task_result.is_finished:
                if self.logger != None:
                    self.logger.info(f"Task={user_task.data.task_id} domain={domain} has been completed.")
                break
            
            self.logger.info(f"Waiting for the task={user_task.data.task_id} domain={domain} to be completed.")

        return task_result
    
    async def get_complete_data_for_domains(self, domains, callback_url:str="", callback_success=None, callback_error=None) -> List[SimilarWebTaskResultModel]:
        
        result = []
        max_tries = 3

        for domain in domains:
            last_exception = None
            for i in range(max_tries):
                try:
                    r = await self.get_complete_data_for_domain(domain, callback_url)
                    last_exception = None
                    result.append(r)
                    if callback_success is not None:
                        callback_success(r)
                    break
                except Exception as ex:
                    last_exception = ex

            if last_exception is not None:
                error_message = f"Cannot get data for domain={domain}. Try again or contact us hello@letsscrape.com"
                self.logger.error(error_message, last_exception)
                if callback_error is not None:
                    callback_error(last_exception)

        return result

    async def get_complete_data_task(self, domain:str, callback_url:str="") -> SimilarWebCompleteDataTaskModel:
        """
        Creates task in the system. The task takes a while to complete, so you can check its
        status by calling GetTaskResultAsync or set a callbackUrl where the result will be sent.
        About callbacks you can read more here https://rapidapi.com/letsscrape/api/similarweb-working-api/tutorials/use-callbacks-when-using-async-endpoints!
        :param domain: domain
        :param callback_url: url where to send response (domain data)
        """
        path = f"/similarweb/GetCompleteDataAsync?domain={domain}&callback_url={callback_url}"
        response_data = await self.__get_request(path=path)
        response = SimilarWebCompleteDataTaskModel.parse_obj(response_data)
        return response

    async def get_task_result(self, task_id) -> SimilarWebTaskResultModel:
        """ 
        After calling GetCompleteDataAsync just use this method to get the result.
        """
        path = f"/similarweb/GetTaskResult?task_id={task_id}"
        response_data = await self.__get_request(path=path)        
        response = SimilarWebTaskResultModel.parse_obj(response_data)
        return response

    async def get_task_result(self, task_id) -> SimilarWebTaskResultModel:
        """ 
        After calling GetCompleteDataAsync just use this method to get the result.
        """
        path = f"/similarweb/GetTaskResult?task_id={task_id}"
        response_data = await self.__get_request(path=path)        
        response = SimilarWebTaskResultModel.parse_obj(response_data)
        return response

    async def get_my_tasks(self, task_status: TaskStatus) -> SimilarWebTaskResultModel:
        """ 
        Returns the list of you all tasks.
        """
        ts = "" if task_status == TaskStatus.ALL else str(task_status)
        path = f"/similarweb/GetMyTasks?task_status={ts}"
        response_data = await self.__get_request(path=path)        
        response = SimilarWebMyTasksModel.parse_obj(response_data)
        return response
    
    async def cancel_task(self, task_id:str) -> SimilarWebCancelTaskModel:
        """
        Cancels created task
        """
        path = f"/similarweb/CancelTask?task_id={task_id}"
        response_data = await self.__get_request(path=path)        
        response = SimilarWebCancelTaskModel.parse_obj(response_data)
        return response
