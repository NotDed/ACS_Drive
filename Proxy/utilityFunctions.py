def totalStorage(svs):
  return sum(list(svs.values()))

def checkStorage(svs, parts):
  return totalStorage(svs) >= parts

def getPercentages(svs):
  percentages = {}
  total = totalStorage(svs)
  if total > 0:
    for ip, parts in svs.items():
      if parts > 0:
        percentages[ip] = (parts/total)
        
  return percentages

def makePartitions(svs, parts):
  partitions = {}
  if checkStorage(svs, parts):
    percentages = getPercentages(svs)
    for ip, percentage in percentages.items():
      partitions[ip] = int(parts*percentage)
      
    excedent =  parts - totalStorage(partitions)
    return partitions, round(excedent)
  else:
    return partitions, 0

def distributeExcedent(svs, partitions, excedent):
  fixedPartitions = partitions.copy()
  distributed = 0
  if excedent <= 0:
    return fixedPartitions

  while True:
    rejected = 0
    for ip in fixedPartitions.keys():
      if svs[ip] - (fixedPartitions[ip] + 1) >= 0:
        fixedPartitions[ip] += 1
        distributed += 1

        if distributed == excedent:
          return fixedPartitions

      else:
        rejected += 1

    if rejected == len(fixedPartitions):
      return {}
  
def trimPartitions(partitions):
  newPartitions = {}
  for ip, parts in partitions.items():
    if parts > 0:
      newPartitions[ip] = parts

  return newPartitions

def indexPartitions(partitions):
  indexedPartitions = {}
  actualRange = 0
  for ip, parts in partitions.items():
    indexedPartitions[ip] = list(range(actualRange, actualRange + parts))
    actualRange += parts
    
  return indexedPartitions

def verifyParitions(svs, partitions):
  for ip, parts in partitions.items():
    if svs[ip] - parts < 0:
      return False
  return True

def getPartitions(svs, parts):
  balancedPartitions = {}
  if checkStorage(svs, parts):
    partitions, excedent = makePartitions(svs, parts)
    balancedPartitions = distributeExcedent(svs, partitions, excedent)
    balancedPartitions = trimPartitions(balancedPartitions)
    if not verifyParitions(svs, balancedPartitions):
      return {}

  balancedPartitions = indexPartitions(balancedPartitions)
  
  return balancedPartitions