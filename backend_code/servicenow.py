from imports import *
from classes import *
from fields import *
class ServiceNowAPI:
    def __init__(self, auth_manager: AuthManager, llm: AzureChatOpenAI):
        self.auth_manager = auth_manager
        self.llm = llm
        self.query_parser_prompt = self._create_query_parser_prompt()
        self.response_formatter_prompt = self._create_response_formatter_prompt()

    def _create_query_parser_prompt(self):
        """Create enhanced prompt template with detailed parameter handling"""
        template = """
        You are an expert ServiceNow analyst. Analyze the following question and determine the appropriate query structure.
        
        Available Tables and Fields:
        INCIDENT TABLE: {incident_fields}
        PROBLEM TABLE: {problem_fields}
        
        Special Parameter Handling:
        1. Assignment Fields:
        - assigned_to: Individual user assignment
        - assignment_group: Group assignment
        - additional_assignee_list: Additional assignees
        - reassignment_count: Number of reassignments
        
        2. State and Phase Fields:
        - state: Current state (New, In Progress, Closed, etc.)
        - phase: Current phase (Requested, Planning, Implementation, etc.)
        - phase_state: State within the current phase
        
        3. Time and Duration Fields:
        - opened_at: Creation timestamp
        - closed_at: Closure timestamp
        - work_start: Actual start time
        - work_end: Actual end time
        - business_duration: Duration in business hours
        - expected_start: Planned start date
        - start_date: Scheduled start
        - end_date: Scheduled end
        
        4. Priority and Impact Fields:
        - impact: Impact level (1-High, 2-Medium, 3-Low)
        - urgency: Urgency level
        - priority: Calculated priority
        - escalation: Escalation status
        
        5. Configuration Items:
        - cmdb_ci: Related configuration item
        - business_service: Affected business service
        - service_offering: Related service offering
        
        6. Notes and Comments:
        - work_notes: Technical notes
        - comments_and_work_notes: Combined notes
        - review_comments: Review feedback
        - additional_comments: Extra notes
        
        7. Approval and Review:
        - approval_set: Approval status
        - review_status: Current review state
        - review_date: Date of review
        - cab_recommendation: Change Advisory Board input
        
        Question: {question}

        Analysis Steps:
        1. Identify query type (incident/problem/combined)
        2. Determine specific parameters needed
        3. Consider related records and their parameters
        4. Apply appropriate conditions and filters
        5. Select relevant return fields
        6. Determine sorting and limiting

        Respond with a JSON structure:
        {{
            "query_type": "incident" or "problem" or "combined",
            "incident_query": {{
                "sysparm_query": "detailed query conditions",
                "sysparm_fields": "specific fields to return",
                "sysparm_limit": limit,
                "sysparm_display_value": "true",
                "sysparm_order_by": "field_name",
                "sysparm_order_by_direction": "DESC/ASC"
            }},
            "problem_query": {{
                "sysparm_query": "detailed query conditions",
                "sysparm_fields": "specific fields to return",
                "sysparm_limit": limit,
                "sysparm_display_value": "true",
                "sysparm_order_by": "field_name",
                "sysparm_order_by_direction": "DESC/ASC"
            }},
            "include_related_data": {{
                "incidents": boolean,
                "tasks": boolean,
                "affected_cis": boolean,
                "change_requests": boolean,
                "work_notes": boolean,
                "approvals": boolean
            }},
            "field_display": {{
                "show_assignment_details": boolean,
                "show_timestamps": boolean,
                "show_notes": boolean,
                "show_approval_info": boolean
            }},
            "explanation": "Detailed explanation of query structure and parameter handling"
        }}
        """
        return PromptTemplate(
            input_variables=["question", "incident_fields", "problem_fields"],
            template=template
        )

    def _create_response_formatter_prompt(self):
        """Create prompt template for formatting responses into human-readable text"""
        template = """
        You are a ServiceNow expert assistant. Convert the following ServiceNow query results into a clear, human-readable response.

        Original Question: {original_question}
        
        Query Results: {query_results}
        
        Instructions:
        1. Provide a natural, conversational response that directly answers the user's question
        2. Present the information in a clear, organized manner
        3. Use bullet points or numbered lists when appropriate for readability
        4. Include relevant details like ticket numbers, states, priorities, descriptions
        5. If no results were found, explain this clearly
        6. Summarize key findings at the end if there are multiple results
        7. Use professional but friendly language
        8. Format dates and times in a readable format
        9. Explain technical terms if necessary
        10. Highlight important information like high-priority incidents or critical problems

        Example format:
        "Based on your query, I found [number] incidents/problems. Here's what I discovered:

        [Detailed information organized clearly]

        Summary: [Brief overview of key findings]"

        Provide only the formatted response text, no additional metadata or JSON.
        """
        return PromptTemplate(
            input_variables=["original_question", "query_results"],
            template=template
        )

    def get_llm_parsed_query(self, question: str) -> Dict:
        """Use LLM to parse natural language query into ServiceNow API parameters"""
        output_parser = JsonOutputParser()
        chain = (
            RunnablePassthrough()
            | self.query_parser_prompt
            | self.llm
            | output_parser
        )
        
        try:
            return chain.invoke({
                "question": question,
                "incident_fields": ", ".join(INCIDENT_FIELDS),
                "problem_fields": ", ".join(PROBLEM_FIELDS)
            })
        except Exception as e:
            print(f"Query parsing error: {str(e)}")
            return None

    def format_response_to_text(self, original_question: str, query_results: Dict) -> str:
        """Convert query results to human-readable text using LLM"""
        output_parser = StrOutputParser()
        chain = (
            RunnablePassthrough()
            | self.response_formatter_prompt
            | self.llm
            | output_parser
        )
        
        try:
            return chain.invoke({
                "original_question": original_question,
                "query_results": str(query_results)
            })
        except Exception as e:
            print(f"Response formatting error: {str(e)}")
            return f"I found some results for your query, but encountered an error formatting the response: {str(e)}"

    def process_query(self, question: str, format_response: bool = True) -> Dict[str, Any]:
        """Process natural language query with improved response structure"""
        try:
            parsed_query = self.get_llm_parsed_query(question)
            if not parsed_query:
                error_response = {
                    "query_type": "unknown",
                    "explanation": "Failed to parse query",
                    "api_calls": [],
                    "results": []
                }
                
                if format_response:
                    return {
                        "formatted_response": "I'm sorry, I couldn't understand your query. Could you please rephrase your question about ServiceNow incidents or problems?",
                        "raw_data": error_response
                    }
                return error_response

            query_type = parsed_query["query_type"]
            results = []
            api_calls = []

            if query_type == "problem" or query_type == "combined":
                # First API call to get problem details
                problem_query = {
                    "sysparm_query": parsed_query["problem_query"]["sysparm_query"],
                    "sysparm_fields": "sys_id,number,state,short_description,related_incidents,priority,opened_by,opened",
                    "sysparm_display_value": "true"
                }
                
                api_calls.append({
                    "endpoint": "/api/now/v2/table/problem",
                    "params": problem_query
                })
                
                problem_results = self.make_request("/api/now/v2/table/problem", problem_query)
                
                for problem in problem_results.get("results", []):
                    problem_data = {
                        "record_type": "problem",
                        "problem_details": {
                            "number": problem.get("number"),
                            "state": problem.get("state"),
                            "description": problem.get("short_description"),
                            "priority": problem.get("priority"),
                            "opened_by": problem.get("opened_by"),
                            "opened": problem.get("opened")
                        },
                        "related_incidents": []
                    }
                    
                    # Second API call to get related incidents
                    if problem.get("sys_id"):
                        incident_query = {
                            "sysparm_query": f"problem_id={problem['sys_id']}",
                            "sysparm_fields": "number,short_description,state,priority,sys_id,assigned_to,assignment_group",
                            "sysparm_display_value": "true"
                        }
                        
                        api_calls.append({
                            "endpoint": "/api/now/v2/table/incident",
                            "params": incident_query
                        })
                        
                        related_incidents = self.make_request("/api/now/v2/table/incident", incident_query)
                        problem_data["related_incidents"] = related_incidents.get("results", [])
                    
                    results.append(problem_data)

            elif query_type == "incident":
                incident_query = parsed_query["incident_query"]
                # Ensure we get more useful fields for better formatting
                if "sysparm_fields" in incident_query:
                    additional_fields = ",opened_by,opened,assigned_to,assignment_group"
                    if additional_fields not in incident_query["sysparm_fields"]:
                        incident_query["sysparm_fields"] += additional_fields
                
                api_calls.append({
                    "endpoint": "/api/now/v2/table/incident",
                    "params": incident_query
                })
                
                incident_results = self.make_request("/api/now/v2/table/incident", incident_query)
                
                for incident in incident_results.get("results", []):
                    results.append({
                        "record_type": "incident",
                        "incident_details": {
                            "number": incident.get("number"),
                            "state": incident.get("state"),
                            "description": incident.get("short_description"),
                            "priority": incident.get("priority"),
                            "opened_by": incident.get("opened_by"),
                            "opened": incident.get("opened"),
                            "assigned_to": incident.get("assigned_to"),
                            "assignment_group": incident.get("assignment_group")
                        }
                    })

            response_data = {
                "query_type": query_type,
                "explanation": parsed_query.get("explanation", ""),
                "api_calls": api_calls,
                "results": results,
                "total_results": len(results)
            }

            if format_response:
                formatted_text = self.format_response_to_text(question, response_data)
                return {
                    "formatted_response": formatted_text,
                    "raw_data": response_data
                }
            
            return response_data

        except Exception as e:
            print(f"Error processing query: {str(e)}")
            error_response = {
                "query_type": "unknown",
                "explanation": "An error occurred while processing the query",
                "api_calls": [],
                "results": [],
                "error": str(e)
            }
            
            if format_response:
                return {
                    "formatted_response": f"I encountered an error while processing your query: {str(e)}. Please try rephrasing your question.",
                    "raw_data": error_response
                }
            return error_response

    def make_request(self, endpoint: str, params: Dict) -> Dict[str, Any]:
        """Make authenticated request to ServiceNow API with improved error handling"""
        url = f"{self.auth_manager.auth_config.instance_url}{endpoint}"
        
        try:
            response = requests.get(
                url, 
                headers=self.auth_manager._get_headers(), 
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get("result"):
                return {"results": [], "total_count": 0}
                
            results = data["result"] if isinstance(data["result"], list) else [data["result"]]
            return {
                "results": results,
                "total_count": len(results)
            }
            
        except requests.exceptions.RequestException as e:
            print(f"ServiceNow API request failed: {str(e)}")
            return {"results": [], "total_count": 0}