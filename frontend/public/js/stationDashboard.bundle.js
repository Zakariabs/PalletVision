document.addEventListener("DOMContentLoaded",(function(){fetch("/api/station-dashboard").then((function(t){return t.json()})).then((function(t){document.getElementById("station-name").textContent=t.station_name;var e=document.getElementById("station-status");e.classList.add(t.status.class),e.querySelector(".status-indicator").textContent=t.status.text;var n=document.getElementById("inference-requests");n.innerHTML="",t.inference_requests.forEach((function(t){var e="\n                    <tr>\n                        <td>".concat(t.answer_timestamp,"</td>\n                        <td>").concat(t.pallet_type,"</td>\n                        <td>\n                            ").concat(t.initial_image?'<img src="'.concat(t.initial_image,'" alt="Initial Image" class="table-image">'):'<span class="text-muted">No Image</span>',"\n                        </td>\n                        <td>\n                            ").concat(t.inferred_image?'<img src="'.concat(t.inferred_image,'" alt="Inferred Image" class="table-image">'):'<span class="text-muted">No Image</span>',"\n                        </td>\n                        <td>").concat(t.confidence_level,"%</td>\n                    </tr>\n                ");n.insertAdjacentHTML("beforeend",e)}))})).catch((function(t){return console.error("Error fetching station dashboard data:",t)}))}));