(()=>{var e=localStorage.getItem("jwtToken");fetch("http://127.0.0.1:5000/api/inference_requests",{headers:{Authorization:"Bearer ".concat(e)}}).then((function(e){if(!e.ok)throw new Error("Failed to fetch inference requests");return e.json()})).then((function(e){!function(e){var t=document.getElementById("inference-requests");t.innerHTML="",e.forEach((function(e){var n="\n            <tr>\n                <td>".concat(new Date(e.answer_time).toLocaleString(),"</td>\n                <td>").concat(e.station_name,"</td>           \n                <td>").concat(e.pallet_type,"</td>\n                <td>\n                    ").concat(e.initial_image_path?'<img src="'.concat(e.initial_image_path.replace("/app/app/ai_service/images/","http://localhost:5000/images/"),'" alt="Initial Image" class="table-image">'):'<span class="text-muted">No Image</span>',"\n                </td>\n                <td>\n                    ").concat(e.inferred_image_path?'<img src="'.concat(e.inferred_image_path.replace("/app/app/ai_service/","http://localhost:5000/images/"),'" alt="Inferred Image" class="table-image">'):'<span class="text-muted">No Image</span>',"\n                </td>\n                <td>").concat((100*e.confidence_level).toFixed(2),"%</td>\n            </tr>\n        ");t.insertAdjacentHTML("afterbegin",n)}))}(e)})).catch((function(e){return console.error("Error fetching inference requests:",e)}))})();