GET_ORG_VISIT_DURATION = """
            query getOrgDurationOfVisits($id: ID, $from: DateTime!, $to: DateTime!){
                organization: getOrganization(id: $id) {
                durationOfVisits(
                    from: $from, to: $to) {
                        visitDuration: hPerDay,
                        visitsCount: clientCount, 
                        visitsPct: percClient,
                        countryRegion
                     }
                }
            }
        """

GET_ORG_VISIT_FREQ = """
        query getOrgFrequencyOfVisits($id: ID, $from: DateTime!, $to: DateTime!){
            organization: getOrganization(id: $id) {
            frequencyOfVisits(
                from: $from, to: $to) {
                    visitFrequency: daysPerWeek,
                    visitsCount: clientCount,
                    visitsPerc: percClient,
                    countryRegion
                }
            }
        }
        """

GET_LOCATION_STATS_DAILY = """
                    query get_building_occupancy_stats_daily(
                        $id: ID!,
                        $from: DateTime!,
                        $to: DateTime!
                        $capacityType: String
                    ) {
                        location(id: $id) {
                            occupancy{
                                daily(
                                    from: $from,
                                    to: $to,
                                    capacityType: $capacityType,
                                ) {
                                    date, 
                                    peakCount,
                                    avgCount,
                                    capacity,
                                    adjustedCapacity,
                                    capacityPct,
                                    uniqueCount
                                }
                            }
                        }
                    }
                        """

GET_LOCATION = """
                    query getBuilding($buildingid: ID){
                        getBuilding(id: $buildingid)
                        {
                            id,
                            workingDays,
                            name,
                            capacity,
                            currentAdjCapacityAbs,
                            workstationsCapacity,
                            totalSeatsCapacity,
                            numberOfDesks,
                            address,
                            timeZone,
                            lat,
                            lng,
                            organizationId,
                            organization{id, name},
                            floors{id, vendorFloorId, buildingId, createdAt, number, name, capacity, workstationsCapacity, totalSeatsCapacity, sqm, floorplanURL, rotation, neCorner, swCorner},
                            rentPriceSQM,
                            currency,
                            area,
                            operationStartTime,
                            operationEndTime,
                            measurementUnits,
                            targetOccupancy,
                            country,
                            countryRegion,
                            euroPerKWH,
                            pulsePerKW,
                            co2PerSQM,
                            tags
                        }
                    }
                """

GET_LOCATION_OCCUPANCY_HOURLY = """
                query getBuildingMerakiHourlyData(
                        $id: ID!,
                        $from: DateTime!,
                        $to: DateTime!,
                        $floorId: String,
                        $floorAreaId: Int,
                        $capacityType: String
                    ) {
                        location(id: $id) {
                            occupancy{
                                hourly(
                                    from: $from,
                                    to: $to,
                                    floorId: $floorId,
                                    floorAreaId: $floorAreaId,
                                    capacityType: $capacityType
                                ) {
                                    hour, 
                                    occupancy: uniqueCount
                                    capacity
                                    adjustedCapacity
                                    capacityPct
                                }
                            }
                        }
                    }

                """

GET_FLOOR_HEATMAP_KPI = """
                       query getFloorHeatmapKPI($floorId: String, $startDate: String, $endDate: String)
                       {
                           getFloorHeatmapKPI(
                            floorId: $floorId,
                            startDate: $startDate,
                            endDate : $endDate,
                            resampleBy : 5
                        ){
                        floorAreaId,
                        maxDevices,
                        avgDevices,
                        maxTimeSpentMinutes,
                        avgTimeSpentMinutes,
                        minTimeSpentMinutes,
                        maxHumans,
                        avgHumans,
                        avgOcuppancy,
                        frequencyOfUse,
                        utilization
                    }}
                    """

GET_FLOOR_METADATA = """
                query readFloor($basking_floor_id: ID){
                    getFloor(id: $basking_floor_id) {
                        id, 
                        number, 
                        name, 
                        sqm, 
                        neCorner, 
                        swCorner, 
                        rotation, 
                        capacity,
                        buildingId
                    }
                }
                """

GET_FLOOR_AREAS = """
                query readFloorArea($basking_floor_id: String){
                        getFloorArea(floorId: $basking_floor_id) {
                            id, 
                            name, 
                            capacity, 
                            geometry, 
                            areaTagId, 
                            tag{id, name}
                        }
                    }
                """

GET_ADJUSTED_CAPACITY = """
                   query readCapacity($locationId: ID!){
                        getCapacity(locationId: $locationId) {
                            id,
                            capacity,
                            start,
                            end,
                            buildingId:locationId,
                            floorId,
                            areaId
                        }
                    }
        """

GET_USER_LOCATIONS = """
                    query getUserBuildings{
                        viewer{
                            buildings{
                                id, name, address, capacity, timeZone, hasMeraki, lat, lng, organizationId, tags
                                }
                            }
                        }
                """

GET_LOCATION_VISIT_DURATION = """
                    query duration(
                        $id: ID!,
                        $from: DateTime!,
                        $to: DateTime!,
                        $capacityType: String
                    ) {
                        location(id: $id) {
                            occupancy{
                                duration(
                                    from: $from, 
                                    to: $to,
                                    capacityType: $capacityType
                                ) {
                                    visitDuration: hoursCount, 
                                    visitsCount: clientsCount,
                                    visitsPerc: clientsPct
                                }
                            }
                        }
                    }       
                """

GET_LOCATION_VISIT_FREQ = """
                    query duration(
                        $id: ID!,
                        $from: DateTime!,
                        $to: DateTime!
                        $capacityType: String
                    ) {
                        location(id: $id) {
                            occupancy{
                                daysPerWeek(
                                    from: $from, 
                                    to: $to,
                                    capacityType: $capacityType
                                ) {
                                    visitFrequency: daysPerWeek, 
                                    visitsCount: clientsCount,
                                    visitsPct: clientsPct
                                }
                            }
                        }
                    }       
                """

GET_ORG_HOTELING = """
                   query getHotelingbyOrg(
                       $id: ID,
                       $startDate: String!, 
                       $endDate: String!
                   ){
                       organization:getOrganization(id: $id){
                           hoteling(startDate: $startDate, 
                                   endDate: $endDate) {
                               from,
                               to,
                               count,
                               country,
                               countryRegion
                           }
                       }
                   }
               """

GET_ORG_DETAILS = """
                    query getOrganization(
                        $id: ID
                    ){
                        organization: getOrganization(id: $id) {
                            id, name   
                        }  
                    }
                """

GET_USER_ORGS = """
                query getUserOrgs {
                    viewer{
                        organizationId, 
                        organizations{
                            id, 
                            name 
                        }
                    }
                }
                """

GET_LOCATION_POPULAR_VISIT_DAYS = """
             query popularDays(
                $id: ID!,
                $from: DateTime!,
                $to: DateTime!,
                $capacityType: String
            ) {
                location(id: $id) {
                    occupancy{
                        popularDaysOfVisit(
                            from: $from, 
                            to: $to,
                            capacityType: $capacityType
                        ) {
                            visitWeekday: dayOfWeek, 
                            visitsCount: clientsCount,
                            visitsPct: clientsPct
                        }
                    }
                }
            }
        """

GET_INSIGHTS = """
            query getInsights($id: ID!, $from: DateTime!, $to: DateTime!){
                getBuildingInsights(id: $id, from: $from, to: $to) {
                    buildingId,
                    monthlyRent,
                    capacity,
                    occupancyPeakMax,
                    occupancyPeakMaxPct,
                    occupancyPeakAvgPct,
                    opportunitySeats,
                    opportunitySeatsPct,
                    adjCapacityPct,
                    targetOccupancyPct,
                    opportunitySpace,  // in m2
                    opportunitySpacePct,
                    opportunityPeopleCount,
                    staffAllocationIncrease,
                    currencySymbol,
                    lengthUnits,
                    peopleImpact {
                        occupancyPeakAvgPct,
                        occupancyPeakMaxPct,
                        costSavings,
                        costSavingsStr,
                    }
                     spaceImpact {
                        occupancyPeakAvgPct,
                        occupancyPeakMaxPct,
                        costSavings,
                        costSavingsStr,
                    }
                }
            }
            """

GET_ORG_POPULAR_VISIT_DAYS = """
            query getOrgPopularDaysOfVisits($id: ID, $from: DateTime!, $to: DateTime!){
              organization: getOrganization(id: $id) {
                  popularDaysOfVisits(from: $from, to: $to) { 
                      visitWeekday: dayOfWeek,
                      visitsCount: clientsCount,
                      visitsPct: clientsPct,
                      countryRegion
                      }}
        }
        """

GET_ORG_LOCATIONS = """
        query getOrgLocations($id: Int!) {
        locations: getBuildingsByOrganization(organizationId: $id) {
                  id,
                  name,
                  address,
                  capacity,
                  timeZone,
                  area,
                  rentPriceSQM,
                  organizationId,
                  targetOccupancy,
                  measurementUnits,
                  currency
                  country,
                  countryRegion,
                  hasMeraki,
                  workingDays,
                  operationStartTime,
                  operationEndTime,
                  totalSeatsCapacity,
                  workstationsCapacity,
                  co2PerSQM,
                  tags
                }
              }
        """

GET_USER = """
                query getUser {
                    viewer{ 
                        id,
                        email,
                        name,
                        firstName,
                        lastName,
                        primaryOrgId: organizationId,
                        createdAt, 
                        measurementUnits, 
                        currency, 
                        isAdjCapacityNormalizationEnabled, 
                        disableQueryCache
                    }
                }
                """
