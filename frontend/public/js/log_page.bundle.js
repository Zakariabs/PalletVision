(()=>{var t;t=localStorage.getItem("jwtToken"),fetch("http://127.0.0.1:5000/api/logs",{headers:{Authorization:"Bearer ".concat(t)}}).then((function(t){if(!t.ok)throw new Error("Failed to fetch logs");return t.json()})).then((function(t){!function(t){var n=document.getElementById("logs");n.innerHTML="",t.forEach((function(t){var e="\n            <tr>\n                <td>".concat(new Date(t.timestamp).toLocaleString(),"</td>\n                <td>").concat(t.category,"</td>\n                <td>").concat(t.message,"</td>\n                <td>\n                    ").concat(t.initial_image?'<img src="'.concat(t.initial_image.replace("/app/app/ai_service/images/","http://localhost:5000/images/"),'" alt="Initial Image" class="table-image">'):'<span class="text-muted">No Image</span>',"\n                </td>\n\n            \n            </tr>\n        ");n.insertAdjacentHTML("beforeend",e)}))}(t)})).catch((function(t){console.error("Error fetching logs:",t)}))})();